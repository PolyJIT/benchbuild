"""
The 'sequence analysis' experiment.

Generates a custom sequence for the project and  writes the compile stats
created doing so. Returns the actions executed for the test.
"""
import uuid
import multiprocessing
import logging
import os
from functools import partial
import random
import parse

from benchbuild.utils.actions import (MakeBuildDir, Prepare, Download,
                                      Configure, Build, Clean)
from benchbuild.experiments.compilestats import get_compilestats

from benchbuild.experiments.polyjit import PolyJIT
from benchbuild.utils.run import track_execution
from plumbum import local
from benchbuild.utils.cmd import (mktemp, opt)

DEFAULT_PASS_SPACE = [
    '-targetlibinfo', '-tti', '-tbaa', '-scoped-noalias',
    '-assumption-cache-tracker', '-profile-summary-info', '-forceattrs',
    '-inferattrs', '-ipsccp', '-globalopt', '-domtree', '-mem2reg',
    '-deadargelim', '-domtree', '-basicaa', '-aa', '-instcombine',
    '-simplifycfg', '-pgo-icall-prom', '-basiccg', '-globals-aa', '-prune-eh',
    '-inline', '-functionattrs', '-argpromotion', '-domtree', '-sroa',
    '-early-cse', '-speculative-execution', '-lazy-value-info',
    '-jump-threading', '-correlated-propagation', '-simplifycfg',
    '-domtree', '-basicaa', '-aa', '-instcombine', '-tailcallelim',
    '-simplifycfg', '-reassociate', '-domtree', '-scalar-evolution',
    '-basicaa', '-aa', '-loop-accesses', '-demanded-bits', '-loop-vectorize',
    '-loop-simplify', '-scalar-evolution', '-aa', '-loop-accesses',
    '-loop-load-elim', '-basicaa', '-aa', '-instcombine',
    '-scalar-evolution', '-demanded-bits', '-slp-vectorizer',
    '-simplifycfg', '-domtree', '-basicaa', '-aa', '-instcombine',
    '-loops', '-loop-simplify', '-lcssa', '-scalar-evolution',
    '-loop-unroll', '-instcombine', '-loop-simplify', '-lcssa',
    '-scalar-evolution', '-licm', '-instsimplify', '-scalar-evolution',
    '-alignment-from-assumptions', '-strip-dead-prototypes', '-globaldce',
    '-constmerge', '-verify']
DEFAULT_SEQ_LENGTH = 40
DEFAULT_DEBUG = False
DEFAULT_NUM_ITERATIONS = 10


def get_defaults():
    pass_space = None
    if not pass_space:
        pass_space = DEFAULT_PASS_SPACE

    seq_length = None
    if not seq_length:
        seq_length = DEFAULT_SEQ_LENGTH

    iterations = None
    if not iterations:
        iterations = DEFAULT_NUM_ITERATIONS

    return (pass_space, seq_length, iterations)


def get_args(cmd):
    assert hasattr(cmd, 'cmd')

    if hasattr(cmd, 'args'):
        return cmd.args
    else:
        return get_args(cmd.cmd)


def set_args(cmd, new_args):
    assert hasattr(cmd, 'cmd')

    if hasattr(cmd, 'args'):
        cmd.args = new_args
    else:
        set_args(cmd.cmd, new_args)


def filter_compiler_commandline(cmd, predicate = lambda x : True):
    args = get_args(cmd)
    result = []

    iterator = args.__iter__()
    try:
        while True:
            litem = iterator.__next__()
            if litem in ['-mllvm', '-Xclang', '-o']:
                fst, snd = (litem, iterator.__next__())
                litem = "{0} {1}".format(fst, snd)
                if predicate(litem):
                    result.append(fst)
                    result.append(snd)
            else:
                if predicate(litem):
                    result.append(litem)
    except StopIteration:
        pass

    set_args(cmd, result)


def run_sequence(project, experiment, compiler, key, seq_to_fitness, sequence):
    local_compiler = compiler[sequence, "-polly-detect"]
    with track_execution(local_compiler, project, experiment) as run:
        run_info = run()
        stats = [s for s in get_compilestats(run_info.stderr) \
                 if s['desc'] in [
                     "Number of regions that a valid part of Scop",
                     "The # of regions"
                 ]]
        scops = [s for s in stats if s['component'].strip() == 'polly-detect']
        regns = [s for s in stats if s['component'].strip() == 'region']
        regns_not_in_scops = \
            [max(r['value']-s['value'], 0) for s, r in zip(scops, regns)]

        old_fitness = seq_to_fitness.get(key, 0)
        new_fitness = old_fitness
        for stat in regns_not_in_scops:
            new_fitness = max(old_fitness, int(stat))
        seq_to_fitness[key] = new_fitness


def unique_compiler_cmds(run_f):
    list_compiler_commands = run_f["-###", "-c"]
    _, _, stderr = list_compiler_commands.run()
    stderr = stderr.split('\n')
    for line in stderr:
        res = parse.search('\"{0}\"', line)
        if res and os.path.exists(res[0]):
            results = parse.findall('\"{0}\"', line)
            cmd = res[0]
            args = [x[0] for x in results][1:]

            compiler_cmd = local[cmd]
            compiler_cmd = compiler_cmd[args]
            compiler_cmd = compiler_cmd["-S", "-emit-llvm"]
            yield compiler_cmd


def link_ir(run_f):
    link = local['llvm-link']
    tmp_files = []
    for compiler in unique_compiler_cmds(run_f):
        tmp_file = mktemp("-p", local.cwd)
        tmp_file = tmp_file.rstrip('\n')
        tmp_files.append(tmp_file)
        compiler("-o", tmp_file)
    complete_ir = mktemp("-p", local.cwd)
    complete_ir = complete_ir.rstrip('\n')
    link("-o", complete_ir, tmp_files)
    return complete_ir


def generate_sequences(project, experiment, config,
                       jobs, run_f, *args, **kwargs):
    """
    Generates the custom sequences for a provided application.

    I therfor use the greedy algorithm Christoph Woller used as well.
    For further information look at the greedy.py file in the sequence-analysis
    experiment. The difference of this method to the actual custom generate
    sequence method is that Mr. Woller only returned the best possible sequence.
    We want all the sequences so i copied most of the method but left out the
    finding and filtering of the best/fittest sequence. The fitness of each
    sequence is still calculated to have some data of each sequence to compare
    and analyze in the data base later on.

    Args:
        project: The name of the project the test is being run for.
        experiment: The benchbuild.experiment.
        config: The config from benchbuild.settings.
        jobs: Number of cores to be used for the execution.
        run_f: The file that needs to be execute.
        args: List of arguments that will be passed to the wrapped binary.
        kwargs: Dictonary with the keyword arguments.

        Returns:
        The generated custom sequences as a list.
    """
    log = logging.getLogger()
    seq_to_fitness = multiprocessing.Manager().dict()
    generated_sequences = []
    pass_space, seq_length, iterations = get_defaults()

    def filter_invalid_flags(item):
        filter_list = [
            "-O1", "-O2", "-O3", "-Os", "-O4"
        ]

        prefix_list = ['-o', '-l', '-L']
        result = not item in filter_list
        result = result and not any([item.startswith(x) for x in prefix_list])
        return result

    filter_compiler_commandline(run_f, filter_invalid_flags)
    complete_ir = link_ir(run_f)
    opt_cmd = opt[complete_ir, "-stats"]

    for _ in range(iterations):
        base_sequence = []
        while len(base_sequence) < seq_length:
            sequences = []
            pool = multiprocessing.Pool()

            for flag in pass_space:
                new_sequences = []
                new_sequences.append(list(base_sequence) + [flag])
                if base_sequence:
                    new_sequences.append([flag] + list(base_sequence))

                sequences.extend(new_sequences)
                for seq in new_sequences:
                    run_sequence(project, experiment,
                                 opt_cmd, str(seq), seq_to_fitness, seq)

            pool.close()
            pool.join()
            # sort the sequences by their fitness in ascending order
            sequences.sort(key=lambda s: seq_to_fitness[str(s)])

            fittest = sequences.pop()
            fittest_fitness_value = seq_to_fitness[str(fittest)]
            fittest_sequences = [fittest]

            next_fittest = fittest
            while next_fittest == fittest and len(sequences) > 1:
                next_fittest = sequences.pop()
                if seq_to_fitness[str(next_fittest)] == fittest_fitness_value:
                    fittest_sequences.append(next_fittest)

            base_sequence = random.choice(fittest_sequences)
        generated_sequences.append(base_sequence)

    generated_sequences.sort(key=lambda s: seq_to_fitness[str(s)])

    # TODO: Store generated_sequence in database.
    print(generated_sequences.pop())


class GreedySequences(PolyJIT):
    """
    An experiment that excecutes all projects with PolyJIT support.

    Instead of the actual actions the compile stats for executing them
    are being written into the database.
    This shall become the default experiment for sequence analysis.
    """

    NAME = "pj-seq-greedy"

    def actions_for_project(self, project):
        """Execute the actions for the test."""
        from benchbuild.settings import CFG

        project = PolyJIT.init_project(project)

        actions = []
        project.cflags = ["-mllvm", "-stats"]
        project.run_uuid = uuid.uuid4()
        jobs = int(CFG["jobs"].value())

        project.compiler_extension = partial(
            generate_sequences, project, self, CFG, jobs)

        actions.extend([
            MakeBuildDir(project),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Clean(project)
        ])
        return actions

        actions.extend([
            MakeBuildDir(project),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Clean(project)
        ])
        return actions
