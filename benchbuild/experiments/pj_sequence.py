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
import multiprocessing
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

DEFAULT_CHROMOSOME_SIZE = 20
DEFAULT_POPULATION_SIZE = 20
DEFAULT_GENERATIONS = 50


def get_defaults():
    """Return the defaults for the experiment."""
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


def get_genetic_defaults():
    """Return the needed defaults for the genetic algorithms."""
    chromosome_size = None
    if not chromosome_size:
        chromosome_size = DEFAULT_CHROMOSOME_SIZE

    population_size = None
    if not population_size:
        population_size = DEFAULT_POPULATION_SIZE

    generations = None
    if not generations:
        generations = DEFAULT_GENERATIONS

    return (chromosome_size, population_size, generations)


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
    seq_to_fitness = {}
    _, _, gene_pool = get_defaults()
    chromosome_size, population_size, generations = get_genetic_defaults()

    def simulate_generation(chromosomes, gene_pool, seq_to_fitness):
        """Simulates the change of a population within a single generation."""
        # calculate the fitness value of each chromosome
        with cf.ThreadPoolExecutor(
            max_workers=CFG["jobs"].value() * 5) as pool:

            future_to_fitness = extend_gene_future([], [],
                                                   [], pool)

            for future_fitness in cf.as_completed(future_to_fitness):
                key, fitness = future_fitness.result()
                old_fitness = seq_to_fitness.get(key, 0)
                seq_to_fitness[key] = max(old_fitness, int(fitness))
        # sort the chromosomes by their fitness value
        chromosomes.sort(key=lambda c: seq_to_fitness[str(c)], reverse=True)

        # divide the chromosome into two halves and delete the weakest one
        index_half = len(chromosomes) // 2
        lower_half = chromosomes[:index_half]
        upper_half = chromosomes[index_half:]

        # delete 4 weak chromosomes
        del lower_half[0]
        random.shuffle(lower_half)

        for _ in range(0, 3):
            lower_half.pop()

        # crossover of two genes and filling of the vacancies in the population
        c1 = random.choice(upper_half)
        c2 = random.choice(upper_half)
        half_index = len(c1) // 2

        new_chromosomes = [c1[:half_index] + c2[half_index:],
                           c1[half_index:] + c2[:half_index],
                           c2[:half_index] + c1[half_index:],
                           c2[half_index:] + c1[:half_index]]

        # mutate the fittest chromosome of this generation
        fittest_chromosome = upper_half.pop()
        lower_half = mutate(lower_half, gene_pool, 10)
        upper_half = mutate(upper_half, gene_pool, 5)

        # rejoin all chromosomes
        upper_half.append(fittest_chromosome)
        chromosomes = lower_half + upper_half + new_chromosomes

        return chromosomes, fittest_chromosome


    def extend_gene_future(future_to_fitness, base, chromosomes, pool):
        """Generate the future of the fitness values from the chromosomes."""
        for flag in gene_pool:
            new_chromosomes = []
            new_chromosomes.append(list(base) + [flag])
            if base:
                new_chromosomes.append([flag] + list(base))

            chromosomes.extend(new_chromosomes)
            future_to_fitness.extend(
                [pool.submit(
                    run_sequence, project, experiment, opt_cmd,
                    str(chromosome), seq_to_fitness, chromosome) \
                    for chromosome in new_chromosomes]
            )
        return future_to_fitness

    def generate_random_gene_sequence(gene_pool):
        """Generates a random sequence of genes."""
        genes = []
        for _ in range(chromosome_size):
            genes.append(random.choice(gene_pool))

        return genes


    def delete_duplicates(chromosomes, gene_pool):
        """Deletes duplicates in the chromosomes of the population."""
        new_chromosomes = []
        for chromosome in chromosomes:
            new_chromosomes.append(tuple(chromosome))

        chromosomes = []
        new_chromosomes = list(set(new_chromosomes))
        diff = population_size - len(new_chromosomes)

        if diff > 0:
            for _ in range(diff):
                chromosomes.append(generate_random_gene_sequence(gene_pool))

        for chromosome in new_chromosomes:
            chromosomes.append(list(chromosome))

        return chromosomes


    def mutate(chromosomes, gene_pool, seq_to_fitness, mutation_probability=10):
        """Performs mutation on chromosomes with a certain probability."""
        mutated_chromosomes = []

        for chromosome in chromosomes:
            mutated_chromosome = list(chromosome)
            chromosome_size = len(mutated_chromosomes)
            number_of_different_chromosomes = len(gene_pool) ** chromosome_size

            for i in range(chromosome_size):
                if random.randint(1, 100) <= mutation_probability:
                    mutated_chromosomes[i] = random.choice(gene_pool)

            num_seq = 0

            while str(mutated_chromosome) in seq_to_fitness and num_seq \
                    < number_of_different_chromosomes:
                mutated_chromosome[random.randint(0, chromosome_size - 1)] \
                = random.choice(gene_pool)
                num_seq += 1

            mutated_chromosomes.append(mutated_chromosome)

        return mutated_chromosomes


    filter_compiler_commandline(run_f, filter_invalid_flags)
    complete_ir = link_ir(run_f)
    opt_cmd = opt[complete_ir, "-disable-output", "-stats"]
    chromosomes = []
    fittest_chromosome = []

    for _ in range(population_size):
        chromosomes.append(generate_random_gene_sequence(gene_pool))

    for i in range(generations):
        chromosomes, fittest_chromosome = simulate_generation(chromosomes,
                                                              gene_pool,
                                                              seq_to_fitness)
        if i < generations - 1:
            chromosomes = delete_duplicates(chromosomes, gene_pool)

    persist_sequences([fittest_chromosome])


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
        The generated custom sequence.
    """
    seq_to_fitness = {}
    _, _, gene_pool = get_defaults()
    chromosome_size, population_size, generations = get_genetic_defaults()

    def extend_gene_future(future_to_fitness, base, chromosomes, pool):
        """Generate the future of the fitness values from the chromosomes."""
        for flag in gene_pool:
            new_chromosomes = []
            new_chromosomes.append(list(base) + [flag])
            if base:
                new_chromosomes.append([flag] + list(base))

            chromosomes.extend(new_chromosomes)
            future_to_fitness.extend(
                [pool.submit(
                    run_sequence, project, experiment, opt_cmd,
                    str(chromosome), seq_to_fitness, chromosome) \
                    for chromosome in new_chromosomes]
            )
        return future_to_fitness

    def generate_random_gene_sequence(gene_pool):
        """Generates a random sequence of genes."""
        genes = []
        for _ in range(chromosome_size):
            genes.append(random.choice(gene_pool))

        return genes

    def delete_duplicates(chromosomes, gene_pool):
        """Deletes duplicates in the chromosomes of the population."""
        new_chromosomes = []
        for chromosome in chromosomes:
            new_chromosomes.append(tuple(chromosome))

        chromosomes = []
        new_chromosomes = list(set(new_chromosomes))
        diff = population_size - len(new_chromosomes)

        if diff > 0:
            for _ in range(diff):
                chromosomes.append(generate_random_gene_sequence(gene_pool))

        for chromosome in new_chromosomes:
            chromosomes.append(list(chromosome))

        return chromosomes

    def mutate(chromosomes, gene_pool, seq_to_fitness, mutation_probability=10):
        """Performs mutation on chromosomes with a certain probability."""
        mutated_chromosomes = []

        for chromosome in chromosomes:
            mutated_chromosome = list(chromosome)
            chromosome_size = len(mutated_chromosomes)
            number_of_different_chromosomes = len(gene_pool) ** chromosome_size

            for i in range(chromosome_size):
                if random.randint(1, 100) <= mutation_probability:
                    mutated_chromosomes[i] = random.choice(gene_pool)

            num_seq = 0

            while str(mutated_chromosome) in seq_to_fitness and num_seq \
                    < number_of_different_chromosomes:
                mutated_chromosome[random.randint(0, chromosome_size - 1)] \
                = random.choice(gene_pool)
                num_seq += 1

            mutated_chromosomes.append(mutated_chromosome)

        return mutated_chromosomes

    def simulate_generation(chromosomes, gene_pool, seq_to_fitness):
        """Simulates the change of a population within a single generation."""
        # calculate the fitness value of each chromosome
        with cf.ThreadPoolExecutor(
            max_workers=CFG["jobs"].value() * 5) as pool:

            future_to_fitness = extend_gene_future([], [],
                                                   [], pool)

            for future_fitness in cf.as_completed(future_to_fitness):
                key, fitness = future_fitness.result()
                old_fitness = seq_to_fitness.get(key, 0)
                seq_to_fitness[key] = max(old_fitness, int(fitness))
        # sort the chromosomes by their fitness value
        chromosomes.sort(key=lambda c: seq_to_fitness[str(c)], reverse=True)

        # best 10% of chromosomes survive without change
        num_best = len(chromosomes) // 10
        fittest_chromosome = chromosomes.pop()
        best_chromosomes = [fittest_chromosome]
        for _ in range(num_best - 1):
            best_chromosomes.append(chromosomes.pop())

        # crossover of two genes and filling of the vacancies in the population
        new_chromosomes = []
        num_of_new = population_size - len(best_chromosomes)
        half_index = len(fittest_chromosome) // 2

        while len(new_chromosomes) < num_of_new:
            c1 = random.choice(best_chromosomes)
            c2 = random.choice(best_chromosomes)
            new_chromosomes.append(c1[:half_index] + c2[half_index:])
            if len(new_chromosomes) < num_of_new:
                new_chromosomes.append(c1[half_index:] + c2[:half_index])
            if len(new_chromosomes) < num_of_new:
                new_chromosomes.append(c2[:half_index] + c1[half_index:])
            if len(new_chromosomes) < num_of_new:
                new_chromosomes.append(c2[half_index:] + c1[:half_index])

        # mutate the new chromosomes
        new_chromosomes = mutate(new_chromosomes, gene_pool, seq_to_fitness)

        # rejoin all chromosomes
        chromosomes = best_chromosomes + new_chromosomes

        return chromosomes, fittest_chromosome


    filter_compiler_commandline(run_f, filter_invalid_flags)
    complete_ir = link_ir(run_f)
    opt_cmd = opt[complete_ir, "-disable-output", "-stats"]
    chromosomes = []
    fittest_chromosome = []

    for _ in range(population_size):
        chromosomes.append(generate_random_gene_sequence(gene_pool))

    for i in range(generations):
        chromosomes, fittest_chromosome = simulate_generation(chromosomes,
                                                              gene_pool,
                                                              seq_to_fitness)
        if i < generations - 1:
            chromosomes = delete_duplicates(chromosomes, gene_pool)

    persist_sequences([fittest_chromosome])
    return fittest_chromosome


class Genetic2Sequence(PolyJIT):
    """
    An experiment that excecutes all projects with PolyJIT support.

    Instead of the actual actions the compile stats for executing them
    are being written into the database.

    The sequences are getting generated with the second genetic algorithm.
    """

    NAME = "pj-seq-genetic2-opt"

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
        The generated custom sequence.
    """

    seq_to_fitness = {}
    pass_space, seq_length, _ = get_defaults()

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

    def create_random_sequence(pass_space, seq_length):
        """Creates a random sequence."""
        sequence = []
        for _ in range(seq_length):
            sequence.append(random.choice(pass_space))

        return sequence

    def calculate_neighbours(seq_to_fitness, pass_space):
        """Calculates the neighbours of the specified sequence."""
        neighbours = []
        base_sequence = create_random_sequence(pass_space, seq_length)
        with cf.ThreadPoolExecutor(
            max_workers=CFG["jobs"].value() * 5) as pool:

            future_to_fitness = extend_future([], base_sequence,
                                              [], pool)

            for future_fitness in cf.as_completed(future_to_fitness):
                key, fitness = future_fitness.result()
                old_fitness = seq_to_fitness.get(key, 0)
                seq_to_fitness[key] = max(old_fitness, int(fitness))

            #normally range(len) would be unnecessary but in this case we need
            #it, due to the usage of the i in the second for loop
            for i in range(len(base_sequence)):
                remaining_passes = list(pass_space)
                remaining_passes.remove(base_sequence[i])

                for remaining_pass in remaining_passes:
                    neighbour = list(base_sequence)
                    neighbour[i] = remaining_pass
                    neighbours.append(neighbour)

        return (neighbours, base_sequence)

    def climb():
        """
        Find the best sequence and calculate all of its neighbours. If the
        best performing neighbour and if it is fitter than the base sequence,
        the neighbour becomes the new base sequence. Repeat until the base
        sequence has the best performance compared to its neighbours.
        """
        changed = True

        while changed:
            changed = False

        neighbours, base_sequence = calculate_neighbours(seq_to_fitness,
                                                         pass_space)
        base_sequence_key = str(base_sequence)

        for neighbour in neighbours:
            if seq_to_fitness[base_sequence_key] \
                    > seq_to_fitness[str(neighbour)]:
                base_sequence = neighbour
                base_sequence_key = str(neighbour)
                changed = True

        return base_sequence

    def create_hillclimber_sequence():
        """
        Generate the sequences, starting from a base_sequence, then calculate
        their fitnesses and add the fittest one.

        Return: The fittest generated sequence.
        """

        best_sequence = []
        _, _, iterations = get_defaults()
        seq_to_fitness = multiprocessing.Manager().dict()

        for _ in range(iterations):
            base_sequence = climb()

        if not best_sequence or seq_to_fitness[str(best_sequence)] \
                < seq_to_fitness[str(base_sequence)]:
            best_sequence = base_sequence
        return base_sequence


    filter_compiler_commandline(run_f, filter_invalid_flags)
    complete_ir = link_ir(run_f)
    opt_cmd = opt[complete_ir, "-disable-output", "-stats"]

    best_sequence = create_hillclimber_sequence()
    persist_sequences([best_sequence])


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
