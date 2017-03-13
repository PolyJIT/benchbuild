"""
The 'sequence analysis' experiment.

Generates a custom sequence for the project and  writes the compile stats
created doing so. Returns the actions executed for the test.
"""
import uuid
import os
from functools import partial
import random
import concurrent.futures as cf
import parse

from benchbuild.experiments.compilestats import get_compilestats

from benchbuild.experiments.polyjit import PolyJIT
from benchbuild.settings import CFG
from benchbuild.utils.actions import (MakeBuildDir, Prepare, Download,
                                      Configure, Build, Clean)
from benchbuild.utils.cmd import (mktemp, opt)
from benchbuild.utils.schema import Session
from plumbum import local

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
    def fitness(l, r):
        return max((l - r) / r, 0)

    local_compiler = compiler[sequence, "-polly-detect"]
    _, _, stderr = local_compiler.run(retcode=None)
    stats = [s for s in get_compilestats(stderr) \
                if s['desc'] in [
                    "Number of regions that a valid part of Scop",
                    "The # of regions"
                ]]
    scops = [s for s in stats if s['component'].strip() == 'polly-detect']
    regns = [s for s in stats if s['component'].strip() == 'region']
    regns_not_in_scops = \
        [fitness(r['value'], s['value']) for s, r in zip(scops, regns)]

    return (key, regns_not_in_scops[0]) \
        if len(regns_not_in_scops) > 0 else (key, 0)


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


def filter_invalid_flags(item):
    """Filter our all the unneeded flags for getting the compilestats."""
    filter_list = [
        "-O1", "-O2", "-O3", "-Os", "-O4"
    ]

    prefix_list = ['-o', '-l', '-L']
    result = not item in filter_list
    result = result and not any([item.startswith(x) for x in prefix_list])
    return result


def persist_sequences(sequences):
    """Saves the generated sequences of an algorithm into the database."""
    session = Session()
    for seq in sequences:
        session.add(seq)
    session.commit()


def genetic1_opt_sequences(project, experiment, config,
                           jobs, run_f, *args, **kwargs):
    """
    Generates custom sequences for a provided application using the first of the
    two genetic opt algorithms.

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
    generated_sequences = []
    pass_space, seq_length, iterations = get_defaults()
    filter_compiler_commandline(run_f, filter_invalid_flags)
    complete_ir = link_ir(run_f)
    opt_cmd = opt[complete_ir, "-disable-output", "-stats"]
#generate sequences aka override simulate_generation
    persist_sequences(generated_sequences)


class Genetic1Sequence(PolyJIT):
    """
    An experiment that excecutes all projects with PolyJIT support.

    Instead of the actual actions the compile stats for executing them
    are being written into the database.

    The sequences are getting generated with the first genetic algorithm.
    """

    NAME = "pj-seq-genetic1-opt"

    def actions_for_project(self, project):
        """Execute the actions for the test."""

        project = PolyJIT.init_project(project)

        actions = []
        project.cflags = ["-mllvm", "-stats"]
        project.run_uuid = uuid.uuid4()
        jobs = int(CFG["jobs"].value())

        project.compiler_extension = partial(
            genetic1_opt_sequences, project, self, CFG, jobs)

        actions.extend([
            MakeBuildDir(project),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Clean(project)
        ])
        return actions


def genetic2_opt_sequences(project, experiment, config,
                           jobs, run_f, *args, **kwargs):
    """
    Generates custom sequences for a provided application using the second
    genetic opt algorithm.

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
    generated_sequences = []
    pass_space, seq_length, iterations = get_defaults()
    filter_compiler_commandline(run_f, filter_invalid_flags)
    complete_ir = link_ir(run_f)
    opt_cmd = opt[complete_ir, "-disable-output", "-stats"]
#generate sequences aka override simulation_generation
    persist_sequences(generated_sequences)


class Genetic2Sequence(PolyJIT):
    """
    An experiment that excecutes all projects with PolyJIT support.

    Instead of the actual actions the compile stats for executing them
    are being written into the database.

    The sequences are getting generated with the second genetic algorithm.
    """

    NAME = "pj-seq-genetic2-ot"

    def actions_for_project(self, project):
        """Execute the actions for the test."""

        project = PolyJIT.init_project(project)

        actions = []
        project.cflags = ["-mllvm", "-stats"]
        project.run_uuid = uuid.uuid4()
        jobs = int(CFG["jobs"].value())

        project.compiler_extension = partial(
            genetic2_opt_sequences, project, self, CFG, jobs)

        actions.extend([
            MakeBuildDir(project),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Clean(project)
        ])
        return actions


def hillclimber_sequences(project, experiment, config,
                          jobs, run_f, *args, **kwargs):
    """
    Generates custom sequences for a provided application using the hillclimber
    algorithm.

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
    generated_sequences = []
    pass_space, seq_length, iterations = get_defaults()
    filter_compiler_commandline(run_f, filter_invalid_flags)
    complete_ir = link_ir(run_f)
    opt_cmd = opt[complete_ir, "-disable-output", "-stats"]
    def climb():
        """
        Find the best sequence and calculate all of its neighbours. If the
        best performing neighbour and if it is fitter than the base sequence,
        the neighbour becomes the new base sequence. Repeat until the base
        sequence has the best performance compared to its neighbours.
        """
        seq_to_fitness = {}
#generate sequences aka override climb
    persist_sequences(generated_sequences)


class HillclimberSequences(PolyJIT):
    """
    An experiment that excecutes all projects with PolyJIT support.

    Instead of the actual actions the compile stats for executing them
    are being written into the database.

    The sequences are getting generated with the hillclimber algorithm.
    """

    NAME = "pj-seq-hillclimber"

    def actions_for_project(self, project):
        """Execute the actions for the test."""

        project = PolyJIT.init_project(project)

        actions = []
        project.cflags = ["-mllvm", "-stats"]
        project.run_uuid = uuid.uuid4()
        jobs = int(CFG["jobs"].value())

        project.compiler_extension = partial(
            hillclimber_sequences, project, self, CFG, jobs)

        actions.extend([
            MakeBuildDir(project),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Clean(project)
        ])
        return actions


def greedy_sequences(project, experiment, config,
                     jobs, run_f, *args, **kwargs):
    """
    Generates the custom sequences for a provided application with the greedy
    algorithm.

    I therfor use the greedy algorithm Christoph Woller used as well.
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
    seq_to_fitness = {}
    generated_sequences = []
    pass_space, seq_length, iterations = get_defaults()

    def extend_future(future_to_fitness, base_sequence, sequences, pool):
        """Generate the future of the fitness values from the sequences."""
        for flag in pass_space:
            new_sequences = []
            new_sequences.append(list(base_sequence) + [flag])
            if base_sequence:
                new_sequences.append([flag] + list(base_sequence))

            sequences.extend(new_sequences)
            future_to_fitness.extend(
                [pool.submit(
                    run_sequence, project, experiment, opt_cmd,
                    str(seq), seq_to_fitness, seq) \
                    for seq in new_sequences]
            )
        return future_to_fitness

    def create_greedy_sequences():
        """
        Generate the sequences, starting from a base_sequence, then calculate
        their fitnesses and add the fittest one.

        Return: A list of the fittest generated sequences.
        """
        for _ in range(iterations):
            base_sequence = []
            while len(base_sequence) < seq_length:
                sequences = []

                with cf.ThreadPoolExecutor(
                    max_workers=CFG["jobs"].value() * 5) as pool:

                    future_to_fitness = extend_future([], base_sequence,
                                                      [], pool)

                    for future_fitness in cf.as_completed(future_to_fitness):
                        key, fitness = future_fitness.result()
                        old_fitness = seq_to_fitness.get(key, 0)
                        seq_to_fitness[key] = max(old_fitness, int(fitness))

                # sort the sequences by their fitness in ascending order
                sequences.sort(key=lambda s: seq_to_fitness[str(s)])

                fittest = sequences.pop()
                fittest_fitness_value = seq_to_fitness[str(fittest)]
                fittest_sequences = [fittest]

                next_fittest = fittest
                while next_fittest == fittest and len(sequences) > 1:
                    next_fittest = sequences.pop()
                    if seq_to_fitness[str(next_fittest)] == \
                            fittest_fitness_value:
                        fittest_sequences.append(next_fittest)

                base_sequence = random.choice(fittest_sequences)
            generated_sequences.append(base_sequence)
        return generated_sequences


    filter_compiler_commandline(run_f, filter_invalid_flags)
    complete_ir = link_ir(run_f)
    opt_cmd = opt[complete_ir, "-disable-output", "-stats"]

    generated_sequences = create_greedy_sequences()
    generated_sequences.sort(key=lambda s: seq_to_fitness[str(s)], reverse=True)
    max_fitness = 0
    for seq in generated_sequences:
        cur_fitness = seq_to_fitness[str(seq)]
        max_fitness = max(max_fitness, cur_fitness)
        if cur_fitness == max_fitness:
            print("{0} -> {1}".format(cur_fitness, seq))
    persist_sequences(generated_sequences)


class GreedySequences(PolyJIT):
    """
    An experiment that excecutes all projects with PolyJIT support.

    Instead of the actual actions the compile stats for executing them
    are being written into the database.

    The sequences are getting generated with the greedy algorithm.
    This shall become the default experiment for sequence analysis.
    """

    NAME = "pj-seq-greedy"

    def actions_for_project(self, project):
        """Execute the actions for the test."""

        project = PolyJIT.init_project(project)

        actions = []
        project.cflags = ["-mllvm", "-stats"]
        project.run_uuid = uuid.uuid4()
        jobs = int(CFG["jobs"].value())

        project.compiler_extension = partial(
            greedy_sequences, project, self, CFG, jobs)

        actions.extend([
            MakeBuildDir(project),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Clean(project)
        ])
        return actions
