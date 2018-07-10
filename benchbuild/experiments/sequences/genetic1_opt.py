# !/usr/bin/env python
"""This module represents an optimized variant of the module genetic1.py.

It uses the multiprocessing module instead of the threading module to take
advantage of systems with multiple cores.
"""
import random
import multiprocessing

import benchbuild.experiments.sequences.polly_stats as polly_stats


__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"

# Default values for the population of chromosomes
MIN_POPULATION_SIZE = 10
DEFAULT_CHROMOSOME_SIZE = 20
DEFAULT_POPULATION_SIZE = 20
DEFAULT_GENE_POOL = ['-basicaa', '-mem2reg']
DEFAULT_GENERATIONS = 200

# Should the program print debug information?
print_out = False


def simulate_generations(gene_pool, environment, gen=DEFAULT_GENERATIONS):
    """Simulates a certain number of generations.

    Args:
        gene_pool (list[string]): list of available genes.
        environment (string): the environment for which the fitness should be
            calculated.
        gen (int, optional): the number of generations to simulate.

    Returns:
        Chromosome: the fittest chromosome of the last generation for the
            specified environment.
    """
    seq_to_fitness = multiprocessing.Manager().dict()
    chromosomes = []
    fittest_chromosome = []

    for i in range(DEFAULT_POPULATION_SIZE):
        chromosomes.append(generate_random_gene_sequence(gene_pool))

    for i in range(gen):
        chromosomes, fittest_chromosome = simulate_generation(chromosomes,
                                                              gene_pool,
                                                              environment,
                                                              seq_to_fitness)

        if i < gen - 1:
            chromosomes = delete_duplicates(chromosomes, gene_pool)

    return fittest_chromosome


def simulate_generation(chromosomes, gene_pool, environment, seq_to_fitness):
    """Simulates a single generation change of the population."""
    # 1. calculate fitness value of each chromosome.
    pool = multiprocessing.Pool()

    for chromosome in chromosomes:
        pool.apply_async(calculate_fitness_value, args=(
            chromosome, seq_to_fitness, str(chromosome), environment))

    pool.close()
    pool.join()

    # 2. sort the chromosomes by its fitness value and reverse the list,
    # because the chromosome with the lowest fitness value is the best.
    chromosomes.sort(key=lambda c: seq_to_fitness[str(c)])
    chromosomes = chromosomes[::-1]

    # 3. divide the chromosome into two halves and delete the weakest
    # chromosome.
    index_half = len(chromosomes) // 2
    lower_half = chromosomes[:index_half]
    upper_half = chromosomes[index_half:]

    # 4. delete four more weak chromosomes.
    del lower_half[0]
    random.shuffle(lower_half)

    for _ in range(0, 3):
        lower_half.pop()

    # 5. crossover: fill the four vacancies in the population with new
    # chromosomes. The genes of the new chromosomes are mixtures of the
    # genes of two randomly chosen strong chromosomes.
    c1 = random.choice(upper_half)
    c2 = random.choice(upper_half)
    half_index = len(c1) // 2

    new_chromosomes = [c1[:half_index] + c2[half_index:],
                       c1[half_index:] + c2[:half_index],
                       c2[:half_index] + c1[half_index:],
                       c2[half_index:] + c1[:half_index]]

    # 6. Get the fittest chromosome of this generation and perform
    # mutations on the remaining chromosomes.
    # The mutation probability for the upper half is 5 percent and
    # the mutation probability for the lower half is 10 percent.
    fittest_chromosome = upper_half.pop()
    lower_half = mutate(lower_half, gene_pool, 10)
    upper_half = mutate(upper_half, gene_pool, 5)

    # 7. Rejoin all chromosomes.
    upper_half.append(fittest_chromosome)
    chromosomes = lower_half + upper_half + new_chromosomes

    return chromosomes, fittest_chromosome


def generate_random_gene_sequence(gene_pool):
    """Generates a random sequence of genes."""
    genes = []
    for _ in range(DEFAULT_CHROMOSOME_SIZE):
        genes.append(random.choice(gene_pool))

    return genes


def mutate(chromosomes, gene_pool, mutation_probability):
    """Performs mutations on chromosomes with a certain probability."""
    mutated_chromosomes = []

    for chromosome in chromosomes:
        mutated_chromosome = list(chromosome)
        chromosome_size = len(mutated_chromosome)

        for i in range(chromosome_size):
            if random.randint(1, 100) <= mutation_probability:
                mutated_chromosome[i] = random.choice(gene_pool)

        mutated_chromosomes.append(mutated_chromosome)

    return mutated_chromosomes


def delete_duplicates(chromosomes, gene_pool):
    """Deletes duplicates in the chromosomes of the population."""
    new_chromosomes = []
    for chromosome in chromosomes:
        new_chromosomes.append(tuple(chromosome))

    chromosomes = []
    new_chromosomes = list(set(new_chromosomes))
    diff = DEFAULT_POPULATION_SIZE - len(new_chromosomes)

    if diff > 0:
        for _ in range(diff):
            chromosomes.append(generate_random_gene_sequence(gene_pool))

    for chromosome in new_chromosomes:
        chromosomes.append(list(chromosome))

    return chromosomes


def calculate_fitness_value(sequence, seq_to_fitness, key, program):
    """Calculates the fitness value of the provided sequence.

    This method calculates the fitness of the sequence by using the number
    of regions that are no valid SCoPs if this sequence is used for
    preoptimization before Polly's SCoP detection.

    Args:
        sequence (list[string]): the sequence for that the fitness value should
            be calculated.
        seq_to_fitness (dict): dictionary that stores calculated fitness
            values.
        key (string): the key of the provided sequence for the dictionary.
        program (string): the name of the application this sequence
            should be used for.
    """
    if key not in seq_to_fitness:
        seq_to_fitness[key] = polly_stats.get_amount_of_bad_regions(sequence,
                                                                    program)


def generate_custom_sequence(program, pass_space=DEFAULT_GENE_POOL,
                             debug=False):
    """Generates a custom optimization sequence for a provided application.

    Args:
        program (string): the name of the application a custom sequence should
            be generated for.
        pass_space (list[string], optional): list of passes that should be
            taken into consideration for the generation of the custom
            sequence.
        debug (boolean, optional): True if debug information should be printed;
            False, otherwise.

    Returns:
        list[string]: the generated custom optimization sequence. Each element
            of the list represents one optimization pass.
    """
    global print_out
    print_out = debug
    return simulate_generations(pass_space, program)
