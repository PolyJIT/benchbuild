"""
The 'sequence analysis' experiment suite.

Each experiment generates sequences of flags for a compiler command using an
algorithm that calculates a best sequence in its own way. For calculating the
value of a sequence (called fitness) regions and scops are being compared to
each other and together generate the fitness value of a sequence.
The used metric depends on the experiment, the fitness is being calculated for.

The fittest generated sequences and the compilestats of the whole progress are
then written into a persisted data base for further analysis.
"""
import csv
import os
import random
import concurrent.futures as cf
import multiprocessing
import sys
import parse
import sqlalchemy as sa

import benchbuild.extensions as ext
from benchbuild.experiments.polyjit import PolyJIT
from benchbuild.settings import CFG

from benchbuild.utils.cmd import (mktemp)
from benchbuild.utils.run import track_execution
from benchbuild.reports import Report
from plumbum import local

DEFAULT_PASS_SPACE = [
    '-targetlibinfo', '-tti', '-tbaa', '-scoped-noalias', '-loop-simplify',
    '-assumption-cache-tracker', '-profile-summary-info', '-forceattrs',
    '-inferattrs', '-ipsccp', '-globalopt', '-domtree', '-mem2reg',
    '-deadargelim', '-aa', '-instcombine', '-loop-unroll', '-lcssa',
    '-pgo-icall-prom', '-basiccg', '-globals-aa', '-prune-eh', '-inline',
    '-functionattrs', '-argpromotion', '-sroa', '-licm', '-instsimplify',
    '-early-cse', '-speculative-execution', '-lazy-value-info',
    '-jump-threading', '-correlated-propagation', '-simplifycfg',
    '-basicaa', '-tailcallelim', '-reassociate', '-scalar-evolution',
    '-loop-accesses', '-loop-vectorize', '-loop-load-elim',
    '-demanded-bits', '-slp-vectorizer', '-loops', '-constmerge',
    '-alignment-from-assumptions', '-strip-dead-prototypes', '-globaldce']
DEFAULT_SEQ_LENGTH = 10
DEFAULT_DEBUG = False
DEFAULT_NUM_ITERATIONS = 1

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
    """Returns the needed defaults for the genetic algorithms."""
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
    """Returns the arguments of a command."""
    assert hasattr(cmd, 'cmd')

    if hasattr(cmd, 'args'):
        return cmd.args
    else:
        return get_args(cmd.cmd)


def set_args(cmd, new_args):
    """Sets the arguments of a command."""
    assert hasattr(cmd, 'cmd')

    if hasattr(cmd, 'args'):
        cmd.args = new_args
    else:
        set_args(cmd.cmd, new_args)


def filter_compiler_commandline(cmd, predicate=lambda x: True):
    """Filter unnecessary arguments for the compiler."""
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


def unique_compiler_cmds(run_f):
    """Verifys that compiler comands are not excecuted twice."""
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
    """
    Connect the intermediate representation of llvm with the files that are
    to be compiled.
    """
    link = local['llvm-link']
    tmp_files = []
    for compiler in unique_compiler_cmds(run_f):
        tmp_file = mktemp("-p", local.cwd)
        tmp_file = tmp_file.rstrip('\n')
        tmp_files.append(tmp_file)
        compiler("-o", tmp_file)
    complete_ir = create_ir()
    link("-o", complete_ir, tmp_files)
    return complete_ir


def create_ir():
    """
    Read out the ir to compare it before and after adding a flag from the pass
    to the sequence or work with its returnings.
    """
    complete_ir = mktemp("-p", local.cwd)
    complete_ir = complete_ir.rstrip('\n')
    return complete_ir


def filter_invalid_flags(item):
    """Filter our all flags not needed for getting the compilestats."""
    filter_list = [
        "-O1", "-O2", "-O3", "-Os", "-O4"
    ]

    prefix_list = ['-o', '-l', '-L']
    result = item not in filter_list
    result = result and not any([item.startswith(x) for x in prefix_list])
    return result


def persist_sequence(run, sequence, fitness_val):
    """
    Persist the sequence and its fitness value in the database.

    Args:
        run: The current run we are attached to, with all its information.
        sequence: The fittest sequence generated by an algorithm.
        fitness_val: The fittest algorithm generated by an algorithm.
    """
    from benchbuild.utils import schema as s
    session = run.session
    session.add(s.Sequence(name=str(sequence),
                           value=fitness_val,
                           run_id=run.db_run.id))
    session.commit()


class SequenceReport(Report):
    """Handles the view of the sequences in the database."""

    SUPPORTED_EXPERIMENTS = ["pj-seq-hillclimber", "pj-seq-genetic1-opt",
                             "pj-seq-genetic2-opt", "pj-seq-greedy"]
    QUERY_TOTAL = \
        sa.sql.select([
            sa.column('sequence'),
            sa.column('fitness'),
        ]).select_from(sa.table('sequences'))

    def report(self):
        print("I found the following matching experiment ids")
        print(" \n".join([str(x) for x in self.experiment_ids]))

        qry = SequenceReport.QUERY_TOTAL.unique_params(
            exp_ids=self.experiment_ids)
        yield ("complete",
               ('sequence', 'fitness'),
               self.session.execute(qry).fetchall())

    def generate(self):
        """Generates the output of what is written in the database."""
        for name, header, data in self.report():
            fname = os.path.basename(self.out_path)

            fname = "{prefix}_{name}{ending}".format(
                prefix=os.path.splitext(fname)[0],
                ending=os.path.splitext(fname)[-1],
                name=name)
            with open(fname, 'w') as csv_out:
                print("Writing '{0}'".format(csv_out.name))
                csv_writer = csv.writer(csv_out)
                csv_writer.writerows([header])
                csv_writer.writerows(data)


class RunSequence(ext.ExtractCompileStats):
    """
    Execute and compile a given sequence, to calculate its fitness value
    with a given function and metric.
    """
    def __call__(self, compiler, key, sequence, fitness_func, *args, **kwargs):
        local_compiler = compiler[sequence, "-polly-detect"]
        _, _, stderr = local_compiler.run(retcode=None)
        stats = [s for s in self.get_compilestats(stderr)
                 if s['desc'] in [
                     "Number of regions that a valid part of Scop",
                     "The # of regions"
                 ]]
        scops = [s for s in stats if s['component'].strip() == 'polly-detect']
        regns = [s for s in stats if s['component'].strip() == 'region']
        regns_not_in_scops = [
            fitness_func(r['value'], s['value']) for s, r in zip(scops, regns)
        ]

        if regns_not_in_scops:
            return (key, regns_not_in_scops[0])
        else:
            return (key, sys.maxsize)


class FindFittestSequenceGenetic1(ext.RuntimeExtension):
    def __call__(self, cc, *args, **kwargs):
        """
        Generates custom sequences using the first genetic opt algorithms.

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
        gene_pool, _, _ = get_defaults()
        chromosome_size, population_size, generations = get_genetic_defaults()
        run_info = track_execution(cc, self.project, self.experiment)

        def crossover(upper_half):
            """
            Crossover of two genes.

            This crosses two gense and fills the vacancies in the population by
            using two random chromosomes and recombine their halfs.
            """
            random1 = random.choice(upper_half)
            random2 = random.choice(upper_half)
            half_index = len(random1) // 2

            new_chromosomes = [random1[:half_index] + random2[half_index:],
                               random1[half_index:] + random2[:half_index],
                               random2[:half_index] + random1[half_index:],
                               random2[half_index:] + random1[:half_index]]

            return new_chromosomes

        def simulate_generation(chromosomes, gene_pool, seq_to_fitness):
            """Simulate the change of a population in a single generation."""
            # calculate the fitness value of each chromosome
            jobs = CFG["jobs"].value() * 5
            with cf.ThreadPoolExecutor(jobs) as pool:
                future_to_fitness = extend_gene_future([], chromosomes, pool)

                for future_fitness in cf.as_completed(future_to_fitness):
                    key, fitness = future_fitness.result()
                    old_fitness = seq_to_fitness.get(key, sys.maxsize)
                    seq_to_fitness[key] = min(old_fitness, int(fitness))
            # sort the chromosomes by their fitness value
            chromosomes.sort(key=lambda c: seq_to_fitness[str(c)],
                             reverse=True)

            # divide the chromosome into two halves and delete the weakest one
            index_half = len(chromosomes) // 2
            lower_half = chromosomes[:index_half]
            upper_half = chromosomes[index_half:]

            # delete four weak chromosomes
            del lower_half[0]
            random.shuffle(lower_half)

            for _ in range(0, 3):
                lower_half.pop()

            new_chromosomes = crossover(upper_half)

            # mutate the fittest chromosome of this generation
            fittest_chromosome = upper_half.pop()
            lower_half = mutate(lower_half, gene_pool, 10)
            upper_half = mutate(upper_half, gene_pool, 5)

            # rejoin all chromosomes
            upper_half.append(fittest_chromosome)
            chromosomes = lower_half + upper_half + new_chromosomes

            return chromosomes, fittest_chromosome

        def generate_random_gene_sequence(gene_pool):
            """Generates a random sequence of genes."""
            genes = []
            for _ in range(chromosome_size):
                genes.append(random.choice(gene_pool))

            return genes

        def extend_gene_future(future_to_fitness, chromosomes, pool):
            def fitness(lhs, rhs):
                """Defines the fitnesses metric."""
                return (lhs - rhs) / rhs

            future_to_fitness.extend(
                [pool.submit(self.call_next, opt_cmd, str(chromosome),
                             chromosome, fitness)
                    for chromosome in chromosomes]
            )
            return future_to_fitness

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
                    chromosomes.append(
                        generate_random_gene_sequence(gene_pool))

            for chromosome in new_chromosomes:
                chromosomes.append(list(chromosome))

            return chromosomes

        def mutate(chromosomes, gene_pool, mutation_probability):
            """Performs mutation on chromosomes with a certain probability."""
            mutated_chromosomes = []

            for chromosome in chromosomes:
                mutated_chromosome = list(chromosome)
                chromosome_size = len(mutated_chromosome)

                for i in range(chromosome_size):
                    if random.randint(1, 100) <= mutation_probability:
                        mutated_chromosome[i] = random.choice(gene_pool)

                mutated_chromosomes.append(mutated_chromosome)

            return mutated_chromosomes

        with run_info as run:
            run_info = run()
        filter_compiler_commandline(cc, filter_invalid_flags)
        complete_ir = link_ir(cc)
        from benchbuild.utils.cmd import opt
        opt_cmd = opt[complete_ir, "-disable-output", "-stats"]
        chromosomes = []
        fittest_chromosome = []

        for _ in range(population_size):
            chromosomes.append(generate_random_gene_sequence(gene_pool))

        for i in range(generations):
            chromosomes, fittest_chromosome = simulate_generation(
                chromosomes, gene_pool, seq_to_fitness)
            if i < generations - 1:
                chromosomes = delete_duplicates(chromosomes, gene_pool)

        persist_sequence(run_info, fittest_chromosome,
                         seq_to_fitness[str(fittest_chromosome)])


class Genetic1Sequence(PolyJIT):
    """
    This experiment is part of the sequence generating suite.

    The sequences for Poly are getting generated using the first of two
    genetic algorithms. Only the compilestats are getting written into
    a database for further analysis.

    """

    NAME = "pj-seq-genetic1-opt"

    def actions_for_project(self, project):
        """Execute the actions for the test."""

        project = PolyJIT.init_project(project)
        project.cflags = ["-mllvm", "-stats"]
        cfg = {"jobs": int(CFG["jobs"].value())}

        project.compiler_extension = \
            FindFittestSequenceGenetic1(
                project, self,
                RunSequence(project, self, config=cfg),
                config=cfg)

        return self.default_compiletime_actions(project)


class FindFittestSequenceGenetic2(ext.RuntimeExtension):
    def __call__(self, cc, *args, **kwargs):
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
        gene_pool, _, _ = get_defaults()
        chromosome_size, population_size, generations = get_genetic_defaults()
        run_info = track_execution(cc, self.project, self.experiment)

        def generate_random_gene_sequence(gene_pool):
            """Generates a random sequence of genes."""
            genes = []
            for _ in range(chromosome_size):
                genes.append(random.choice(gene_pool))

            return genes

        def extend_gene_future(future_to_fitness, chromosomes, pool):
            """Extend with future values from the chromosomes."""
            def fitness(lhs, rhs):
                """Defines the fitnesses metric."""
                return (lhs - rhs) / rhs

            future_to_fitness.extend(
                [pool.submit(self.call_next, opt_cmd, str(chromosome),
                             chromosome, fitness)
                 for chromosome in chromosomes]
            )
            return future_to_fitness

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
                    chromosomes.append(
                        generate_random_gene_sequence(gene_pool))

            for chromosome in new_chromosomes:
                chromosomes.append(list(chromosome))

            return chromosomes

        def mutate(chromosomes, gene_pool, mutation_probability):
            """Performs mutation on chromosomes with a certain probability."""
            mutated_chromosomes = []

            for chromosome in chromosomes:
                mutated_chromosome = list(chromosome)
                chromosome_size = len(mutated_chromosome)

                for i in range(chromosome_size):
                    if random.randint(1, 100) <= mutation_probability:
                        mutated_chromosome[i] = random.choice(gene_pool)

                mutated_chromosomes.append(mutated_chromosome)

            return mutated_chromosomes

        def crossover(fittest_chromosome, best_chromosomes):
            """
            Crossover two genes and fill the vacancies in the population by
            taking two of the fittest chromosomes and recombining them.
            """
            new_chromosomes = []
            num_of_new = population_size - len(best_chromosomes)
            half_index = len(fittest_chromosome) // 2

            while len(new_chromosomes) < num_of_new:
                best1 = random.choice(best_chromosomes)
                best2 = random.choice(best_chromosomes)
                new_chromosomes.append(best1[:half_index] + best2[half_index:])
                if len(new_chromosomes) < num_of_new:
                    new_chromosomes.append(
                        best1[half_index:] + best2[:half_index])
                if len(new_chromosomes) < num_of_new:
                    new_chromosomes.append(
                        best2[:half_index] + best1[half_index:])
                if len(new_chromosomes) < num_of_new:
                    new_chromosomes.append(
                        best2[half_index:] + best1[:half_index])

            return new_chromosomes

        def simulate_generation(chromosomes, gene_pool, seq_to_fitness):
            """Simulate the change of a population in a single generation."""
            # calculate the fitness value of each chromosome
            jobs = CFG["jobs"].value() * 5
            with cf.ThreadPoolExecutor(jobs) as pool:
                future_to_fitness = extend_gene_future([], chromosomes, pool)

                for future_fitness in cf.as_completed(future_to_fitness):
                    key, fitness = future_fitness.result()
                    old_fitness = seq_to_fitness.get(key, sys.maxsize)
                    seq_to_fitness[key] = min(old_fitness, int(fitness))
            # sort the chromosomes by their fitness value
            chromosomes.sort(key=lambda c: seq_to_fitness[str(c)],
                             reverse=True)

            # best 10% of chromosomes survive without change
            num_best = len(chromosomes) // 10
            fittest_chromosome = chromosomes.pop()
            best_chromosomes = [fittest_chromosome]
            for _ in range(num_best - 1):
                best_chromosomes.append(chromosomes.pop())

            new_chromosomes = crossover(fittest_chromosome, best_chromosomes)

            # mutate the new chromosomes
            new_chromosomes = mutate(new_chromosomes, gene_pool, 10)

            # rejoin all chromosomes
            chromosomes = best_chromosomes + new_chromosomes

            return chromosomes, fittest_chromosome

        with run_info as run:
            run_info = run()
        filter_compiler_commandline(cc, filter_invalid_flags)
        complete_ir = link_ir(cc)
        from benchbuild.utils.cmd import opt
        opt_cmd = opt[complete_ir, "-disable-output", "-stats"]
        chromosomes = []
        fittest_chromosome = []

        for _ in range(population_size):
            chromosomes.append(generate_random_gene_sequence(gene_pool))

        for i in range(generations):
            chromosomes, fittest_chromosome = \
                simulate_generation(chromosomes, gene_pool, seq_to_fitness)
            if i < generations - 1:
                chromosomes = delete_duplicates(chromosomes, gene_pool)

        persist_sequence(run_info, fittest_chromosome,
                         seq_to_fitness[str(fittest_chromosome)])


class Genetic2Sequence(PolyJIT):
    """
    An experiment that excecutes all projects with PolyJIT support.

    It is part of the sequence generating experiment suite.

    The sequences are getting generated for Poly using another
    than the first genetic algorithm. The compilestats are getting written into
    a database for further analysis.

    """

    NAME = "pj-seq-genetic2-opt"

    def actions_for_project(self, project):
        """Execute the actions for the test."""

        p = PolyJIT.init_project(project)
        p.cflags = ["-mllvm", "-stats"]
        cfg = {"jobs": int(CFG["jobs"].value())}

        p.compiler_extension = \
            FindFittestSequenceGenetic2(
                p, self,
                RunSequence(p, self, config=cfg),
                config=cfg)

        return Genetic2Sequence.default_compiletime_actions(p)


class FindFittestSequenceHillclimber(ext.RuntimeExtension):
    def __call__(self, cc, *args, **kwargs):
        seq_to_fitness = {}
        pass_space, seq_length, iterations = get_defaults()
        run_info = track_execution(cc, self.project, self.experiment)

        def fitness(lhs, rhs):
            """Defines the fitnesses metric."""
            return lhs - rhs

        def extend_future(sequence, pool):
            """
            Generate the future of the fitness values from the sequence.
            """
            neighbours = []
            future_to_fitness = []

            # generate the neighbours of the current base sequence
            for i in range(seq_length):
                remaining_passes = list(pass_space)
                remaining_passes.remove(sequence[i])

                for remaining_pass in remaining_passes:
                    neighbour = list(sequence)
                    neighbour[i] = remaining_pass
                    neighbours.append(neighbour)

                future_to_fitness.extend(
                    [pool.submit(self.call_next, opt_cmd, str(sequence),
                                 sequence, fitness)]
                )

            future_to_fitness.extend(
                [pool.submit(self.call_next,
                             opt_cmd, str(neighbour), neighbour, fitness)
                 for neighbour in neighbours])

            return future_to_fitness, neighbours

        def create_random_sequence(pass_space, seq_length):
            """Creates a random sequence."""
            sequence = []
            for _ in range(seq_length):
                sequence.append(random.choice(pass_space))

            return sequence

        def climb(sequence, seq_to_fitness):
            """
            Find the best sequence and calculate all of its neighbours. If the
            best performing neighbour is fitter than the base sequence,
            the neighbour becomes the new base sequence. Repeat until the base
            sequence has the best performance compared to its neighbours.
            """
            changed = True
            future_to_fitness = []
            base_sequence = sequence
            base_sequence_key = str(sequence)
            with cf.ThreadPoolExecutor(max_workers=CFG["jobs"].value() * 5) \
                    as pool:
                while changed:
                    changed = False
                    future_to_fitness, neighbours = \
                        extend_future(base_sequence, pool)
                    for future_fitness in cf.as_completed(future_to_fitness):
                        key, fitness_val = future_fitness.result()
                        old_fitness = seq_to_fitness.get(key, sys.maxsize)
                        seq_to_fitness[key] = min(old_fitness, fitness_val)

                    for neighbour in neighbours:
                        if seq_to_fitness[base_sequence_key] \
                                > seq_to_fitness[str(neighbour)]:
                            base_sequence = neighbour
                            base_sequence_key = str(neighbour)
                            changed = True

            return base_sequence, seq_to_fitness

        with run_info as run:
            run_info = run()
        filter_compiler_commandline(cc, filter_invalid_flags)
        complete_ir = link_ir(cc)
        from benchbuild.utils.cmd import opt
        opt_cmd = opt[complete_ir, "-disable-output", "-stats"]

        best_sequence = []
        seq_to_fitness = multiprocessing.Manager().dict()

        for _ in range(iterations):
            base_sequence = create_random_sequence(pass_space, seq_length)
            best_sequence, seq_to_fitness = \
                climb(base_sequence, seq_to_fitness)

            if not best_sequence or seq_to_fitness[str(best_sequence)] \
                    > seq_to_fitness[str(base_sequence)]:
                best_sequence = base_sequence

        persist_sequence(run_info,
                         best_sequence,
                         seq_to_fitness[str(best_sequence)])


class HillclimberSequences(PolyJIT):
    """
    This experiment is part of the sequence generating suite.

    The sequences for poly are getting generated using a hillclimber algorithm.
    The ouptut gets thrown away and the statistics of the compiling are written
    into a database to be analyzed later on.

    """

    NAME = "pj-seq-hillclimber"

    def actions_for_project(self, project):
        """Execute the actions for the test."""

        project = PolyJIT.init_project(project)
        project.cflags = ["-mllvm", "-stats"]
        cfg = {'jobs': int(CFG["jobs"].value())}

        project.compiler_extension = \
            FindFittestSequenceHillclimber(
                project, self,
                RunSequence(project, self, config=cfg),
                config=cfg)
        return HillclimberSequences.default_compiletime_actions(project)


class FindFittestSequenceGreedy(ext.RuntimeExtension):
    def __call__(self, cc, *args, **kwargs):
        seq_to_fitness = {}
        generated_sequences = []
        pass_space, seq_length, iterations = get_defaults()
        run_info = track_execution(cc, self.project, self.experiment)

        def extend_future(base_sequence, pool):
            """Generate the future of the fitness values from the sequences."""
            def fitness(lhs, rhs):
                """Defines the fitnesses metric."""
                return lhs - rhs

            future_to_fitness = []
            sequences = []
            for flag in pass_space:
                new_sequences = []
                new_sequences.append(list(base_sequence) + [flag])
                if base_sequence:
                    new_sequences.append([flag] + list(base_sequence))

                sequences.extend(new_sequences)
                future_to_fitness.extend(
                    [pool.submit(
                        self.call_next, opt_cmd, str(seq), seq, fitness)
                     for seq in new_sequences]
                )
            return future_to_fitness, sequences

        def create_greedy_sequences():
            """
            Create an optimal sequence, using a greedy algorithm.

            Return: A list of the fittest generated sequences.
            """

            jobs = CFG["jobs"].value() * 5
            with cf.ThreadPoolExecutor(max_workers=jobs) as pool:
                for _ in range(iterations):
                    base_sequence = []
                    while len(base_sequence) < seq_length:
                        future_to_fitness, sequences = \
                            extend_future(base_sequence, pool)

                        for future_fitness in cf.as_completed(
                                future_to_fitness):
                            key, fitness = future_fitness.result()
                            old_fitness = seq_to_fitness.get(key, sys.maxsize)
                            seq_to_fitness[key] = min(old_fitness, fitness)

                        sequences.sort(key=lambda s: seq_to_fitness[str(s)],
                                       reverse=True)

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

        with run_info as run:
            run_info = run()
        filter_compiler_commandline(cc, filter_invalid_flags)
        complete_ir = link_ir(cc)
        from benchbuild.utils.cmd import opt
        opt_cmd = opt[complete_ir, "-disable-output", "-stats"]

        generated_sequences = create_greedy_sequences()
        generated_sequences.sort(
            key=lambda s: seq_to_fitness[str(s)], reverse=True)
        max_fitness = 0
        for seq in generated_sequences:
            cur_fitness = seq_to_fitness[str(seq)]
            max_fitness = max(max_fitness, cur_fitness)
        fittest_sequence = generated_sequences.pop()
        persist_sequence(run_info, fittest_sequence, max_fitness)


class GreedySequences(PolyJIT):
    """
    This experiment is part of the sequence generating experiment suite.

    Instead of the actual actions the compile stats for executing them
    are being written into the database.
    The sequences are getting generated with the greedy algorithm.
    This shall become the default experiment for sequence analysis.

    """

    NAME = "pj-seq-greedy"

    def actions_for_project(self, project):
        """Execute the actions for the test."""

        project = PolyJIT.init_project(project)
        project.cflags = ["-mllvm", "-stats"]
        cfg = {'jobs': int(CFG["jobs"].value())}

        project.compiler_extension = \
            FindFittestSequenceGreedy(
                project, self,
                RunSequence(project, self, config=cfg),
                config=cfg)

        return GreedySequences.default_compiletime_actions(project)
