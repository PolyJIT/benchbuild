"""
The 'sequence analysis' experiment.

Generates a custom sequence for the project and  writes the compile stats
created doing so. Returns the actions executed for the test.
"""
import uuid
import multiprocessing
import logging

from functools import partial
from benchbuild.utils.actions import (MakeBuildDir, Prepare, Download,
                                    Configure, Build, Run, Clean)

from benchbuild.experiments.polyjit import PolyJIT

DEFAULT_PASS_SPACE = ['-basicaa', '-mem2reg']
DEFAULT_SEQ_LENGTH = 10
DEFAULT_DEBUG = False
DEFAULT_NUM_ITERATIONS = 100

def get_compilestats(prog_out):
    """ Get the LLVM compilation stats from :prog_out:. """
    from parse import compile as c

    stats_pattern = c("{value:d} {component} - {desc}\n")

    for line in prog_out.split("\n"):
        res = stats_pattern.search(line + "\n")
        if res is not None:
            yield res

def collect_compilestats(project, experiment, clang, **kwargs):
    """Collect compilestats and write them into the database persistently."""
    from benchbuild.utils.db import persist_compilestats
    from benchbuild.utils.schema import CompileStat
    from benchbuild.utils.run import track_execution, handle_stdin

    clang = handle_stdin(clang["-mllvm", "-stats"], kwargs)

    with track_execution(clang, project, experiment) as run:
        run_information = run()

    if run_information.retcode == 0:
        stats = []
        for stat in get_compilestats(run_information.stderr):
            compile_s = CompileStat()
            compile_s.name = stat["desc"].rstrip()
            compile_s.component = stat["component"].rstrip()
            compile_s.value = stat["value"]
            stats.append(compile_s)
        persist_compilestats(run_information.db_run,
                             run_information.session,
                             stats)

def generate_sequences(project, experiment, config, jobs, run_f, args, **kwargs):
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
        program: The name of the application the sequence is being generated.
        pass_space: List of passes that should be considered during the
            generating process of the sequence.
        seq_length: The length of the sequence that should be generated.
        iterations: The amount of iterations the algorithm performs to reduce
            possible noise.
        debug: Boolean, if debug information should be printed or not.

        Returns:
        The generated custom sequences as a list.
    """
    from benchbuild.experiments.sequences import greedy
    seq_to_fitness = multiprocessing.Manager().dict()
    generated_sequences = []

    pass_space = None
    if not pass_space:
        pass_space = DEFAULT_PASS_SPACE

    seq_length = None
    if not seq_length:
        seq_length = DEFAULT_SEQ_LENGTH

    iterations = None
    if not iterations:
        iterations = DEFAULT_NUM_ITERATIONS

    debug = None
    if not debug:
        debug = DEFAULT_DEBUG

    log = logging.getLogger()
    for i in range(iterations):
        log.debug("==========================================")
        log.debug("Iteration: " + str(i+1))
        log.debug("==========================================")
        log.debug("Start Greedy Algorithm with" + \
                                  "empty sequence as root...")

        base_sequence = []

        while len(base_sequence) < seq_length:
            log.debug("<=-----------------------------------=>")
            log.debug("Custom Sequence: " + str(base_sequence))
            log.debug("Length: " + str(len(base_sequence)))
            log.debug("---------------------------------------")
            log.debug("Child Sequences: ")
            sequences = []

            pool = multiprocessing.Pool()
            for flag in pass_space:
                # Create new sequence by appending a new flag.
                seq_append = list(base_sequence) + [flag]

                pool.apply_async(
                    greedy.calculate_fitness_value,
                    args=(seq_append, seq_to_fitness, str(seq_append), run_f))
                sequences.append(seq_append)
                log.debug(str(seq_append))

                if base_sequence:
                    # Create a new sequence by depending a new flag.
                    seq_prepend = [flag] + list(base_sequence)
                    pool.apply_async(
                        greedy.calculate_fitness_value, args=(
                        seq_prepend, seq_to_fitness, str(seq_prepend), program))
                    sequences.append(seq_prepend)
                    log.debug(str(seq_prepend))

            pool.close()
            pool.join()
            # sort the sequences by their fitness
            sequences.sort(key=lambda s: seq_to_fitness[str(s)])
            log.debug("<=-----------------------------------=>")
        generated_sequences.append(sequences)

    generated_sequences.sort(key=lambda s: seq_to_fitness[str(s)])
    log.debug("\n...Finished!")
    log.debug(
        "Generated Custom Sequences in " + str(iterations) + " Iterations:")
    if debug:
        sorted_seq = sorted(seq_to_fitness.iteritems(),
                            key=operator.itemgetter(1))
        log.debug('\nBest sequences found over iterations:')
        for i in range(len(sorted_seq)):
            log.debug(sorted_seq.pop())

        log.debug("\n")

    return generated_sequences

class CollisionTest(PolyJIT):
    """
    An experiment that excecutes all projects with PolyJIT support.
    Instead of the actual actions the compile stats for executing them
    are being written into the database.
    This shall become the default experiment for sequence analysis.
    """

    NAME = "pj-seq-test"

    def actions_for_project(self, project):
        """Executes the actions for the test."""
        from benchbuild.settings import CFG

        project = PolyJIT.init_project(project)

        actions = []
        project.cflags = ["-O3", "-Xclang", "-load", "-Xclang",
                          "LLVMPolyJIT.so", "-mllvm", "-polly"]
        project.run_uuid = uuid.uuid4()
        jobs = int(CFG["jobs"].value())
        project.runtime_extension = partial(generate_sequences, project, self, CFG, jobs)
        project.compiler_extension = partial(collect_compilestats,
                                             project,
                                             self)
        actions.extend([
            MakeBuildDir(project),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Run(project),
            Clean(project)
        ])
        return actions
