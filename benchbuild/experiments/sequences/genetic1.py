#!/usr/bin/env python
"""This module supplies a function that can generate custom sequences of
optimization passes for arbitrary programs.

This module provides an implementation of a genetic algorithm presented by
Cooper in his paper "Optimizing for Reduced Code Space using Genetic
Algorithms" (published 1999). The algorithm is used to generate a custom
optimization sequence for an arbitrary application. The resulting sequence
is a list of flags that can be set by the LLVM opt tool. The generated
sequence is meant to be a good flag combination that increases the amount of
code that can be detected by Polly.
"""
import random
import threading
import logging

import benchbuild.experiments.sequences.polly_stats as polly_stats


__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"

# Default values for the population of chromosomes.
MIN_POPULATION_SIZE = 10
DEFAULT_CHROMOSOME_SIZE = 20
DEFAULT_POPULATION_SIZE = 20
DEFAULT_GENE_POOL = ['-basicaa', '-mem2reg']
DEFAULT_GENERATIONS = 200

# Store occurred sequences and their fitness value.
seq_to_fitness = {}

# Should the program print debug information?.
print_out = False


def print_chromosome_list(chromosomes):
    """This helper function just prints a list of chromosomes."""
    for chromosome in chromosomes:
        print(chromosome)


class Chromosome(object):
    """The class Chromosome is used to represent a single chromosome of a
    population. Each chromosome consists of genes and has a fitness value.
    The genes are available optimization flags. The fitness value of a
    chromosome is the number of regions in the application that are no valid
    SCoPs if you call Polly with the flags that are represented by the genes
    of the chromosome. Hence, the lower the better.
    """
    chromosome_number = 0

    def __init__(self, genes, environment):
        """Initializes a chromosome.

        Args:
            genes (list[string]): the genes of this chromosome.
            environment (string): the name of the environment in which the
                chromosome's fitness should be tested. In this case the
                environment is the name of the program in which we want to
                detect SCoPs.
        """
        Chromosome.chromosome_number += 1
        self.chromosome_id = Chromosome.chromosome_number
        self.genes = genes if genes is not None else []
        self.environment = environment
        self.fitness_value = float('inf')

    def __str__(self):
        """Returns a string representation of this chromosome."""
        return (str(self.chromosome_id) + '. Chromosome: Genes: ' + str(
            self.genes) + '; Fitness: ' + str(self.fitness_value))

    def __eq__(self, other):
        """Checks if two chromosomes are equal.

        Returns:
            boolean: true if the environment and the genes of the chromosomes
                are equal; false otherwise.
        """
        if self.environment != other.environment:
            return False

        for i in range(0, len(self.genes)):
            if self.genes[i] != other.genes[i]:
                return False

        return True

    def __hash__(self):
        """Returns the hash value for this chromosome."""
        return hash(('genes', tuple(self.genes), self.environment))

    def calculate_fitness_value(self):
        """Calculates the fitness value of this chromosome."""
        sequence = ''.join(self.genes)
        if sequence in seq_to_fitness:
            self.fitness_value = seq_to_fitness[sequence]
        else:
            self.fitness_value = polly_stats.get_amount_of_bad_regions(
                self.genes, self.environment)


class Population(object):
    """This class represents a population of chromosomes.

    The chromosomes of a population can reproduce and mutate over
    generations. This class provides functionality to simulate the next
    generations of the population.
    """

    def __init__(self, environment, size=DEFAULT_POPULATION_SIZE,
                 gene_pool=DEFAULT_GENE_POOL,
                 chromosome_size=DEFAULT_CHROMOSOME_SIZE):
        """Initializes a new population.

        The first generation of chromosomes of the population is created
        randomly.

        Args:
            environment (string): the environment the chromosomes should live
                in over the generations.
            size (int, optional): the number of chromosomes this population
                should consist of.
            gene_pool (list[string], optional): a list containing all available
                genes.
            chromosome_size (int, optional): the number of genes a chromosome
                should consist of.
        """
        self.gene_pool = gene_pool if gene_pool else DEFAULT_GENE_POOL
        self.size = max(size, MIN_POPULATION_SIZE)
        self.chromosome_size = max(chromosome_size, 0)
        self.generation = 0
        self.fittest_chromosome = None
        self.chromosomes = []
        self.environment = environment

        for _ in range(self.size):
            self.chromosomes.append(
                Chromosome(self.__generate_random_gene_sequence(),
                           self.environment))

    def __str__(self):
        """Prints out a string representation of this population."""
        result = ('---> Population - Generation: ' + str(self.generation)
                  + '<--- \n')
        result += 'Fittest Chromosome: \n' + str(self.fittest_chromosome)

        for chromosome in self.chromosomes:
            result += str(chromosome) + '\n'

        return result

    def simulate_generations(self, generations=DEFAULT_GENERATIONS):
        """Simulates a certain number of generations.

        Args:
            generations (int, optional): the number of generations to simulate.

        Returns:
            Chromosome: the fittest chromosome of the last generation for the
                specified environment.
        """
        for i in range(generations):
            logging.getLogger(__name__).debug(self)
            self.__simulate_generation()

            if i < generations - 1:
                self.__delete_duplicates()

        return self.fittest_chromosome

    def __simulate_generation(self):
        """Simulates a single generation change of the population."""
        global seq_to_fitness

        # 1. calculate fitness value of each chromosome.
        threads = []
        for chromosome in self.chromosomes:
            t = threading.Thread(target=chromosome.calculate_fitness_value())
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

        for chromosome in self.chromosomes:
            key = ''.join(chromosome.genes)
            if key not in seq_to_fitness:
                seq_to_fitness[key] = chromosome.fitness_value

        # 2. sort the chromosomes by its fitness value and reverse the list,
        # because the chromosome with the lowest fitness value is the best.
        self.chromosomes.sort(key=lambda c: c.fitness_value)
        self.chromosomes = self.chromosomes[::-1]

        # 3. divide the chromosome into two halves and delete the weakest
        # chromosome.
        index_half = len(self.chromosomes) // 2
        lower_half = self.chromosomes[:index_half]
        upper_half = self.chromosomes[index_half:]

        # 4. delete four more weak chromosomes.
        del lower_half[0]
        random.shuffle(lower_half)

        for i in range(0, 3):
            lower_half.pop()

        # 5. crossover: fill the four vacancies in the population with new
        # chromosomes. The genes of the new chromosomes are mixtures of the
        # genes of two randomly chosen strong chromosomes.
        c1 = random.choice(upper_half)
        c2 = random.choice(upper_half)
        new_chromosomes = [
            Chromosome(c1.genes[:self.chromosome_size // 2]
                       + c2.genes[self.chromosome_size // 2:],
                       self.environment),
            Chromosome(c1.genes[self.chromosome_size // 2:]
                       + c2.genes[:self.chromosome_size // 2],
                       self.environment),
            Chromosome(c2.genes[:self.chromosome_size // 2]
                       + c1.genes[self.chromosome_size // 2:],
                       self.environment),
            Chromosome(c2.genes[self.chromosome_size // 2:]
                       + c1.genes[:self.chromosome_size // 2],
                       self.environment)]

        # 6. Get the fittest chromosome of this generation and perform
        # mutations on the remaining chromosomes.
        # The mutation probability for the upper half is 5 percent and
        # the mutation probability for the lower half is 10 percent.
        self.fittest_chromosome = upper_half.pop()
        self.__mutate(lower_half, 10)
        self.__mutate(upper_half, 5)

        # 7. Rejoin all chromosomes.
        upper_half.append(self.fittest_chromosome)
        self.chromosomes = lower_half + upper_half + new_chromosomes
        self.generation += 1

    def __generate_random_gene_sequence(self):
        """Generates a random sequence of genes."""
        genes = []
        for _ in range(self.chromosome_size):
            genes.append(random.choice(self.gene_pool))

        return genes

    def __mutate(self, chromosomes, mutation_probability):
        """Performs mutations on chromosomes with a certain probability."""

        for chromosome in chromosomes:
            for i in range(self.chromosome_size):
                if random.randint(1, 100) <= mutation_probability:
                    logging.getLogger(__name__).debug(
                        "---> Mutation in Chromosome %s in gene %d <---",
                        str(chromosome.chromosome_id), i)
                    chromosome.genes[i] = random.choice(self.gene_pool)


    def __delete_duplicates(self):
        """Deletes duplicates in the chromosomes of the population."""
        log = logging.getLogger(__name__)
        log.debug("\n---> Duplicate check <---")

        chromosomes = list(set(self.chromosomes))
        diff = self.size - len(chromosomes)

        if diff > 0:
            log.debug("---> Duplicate(s) found! <---")
            for _ in range(diff):
                chromosomes.append(
                    Chromosome(self.__generate_random_gene_sequence(),
                               self.environment))
        else:
            log.debug("---> No duplicates found! <---")

        self.chromosomes = chromosomes


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
    return Population(gene_pool=pass_space,
                      environment=program).simulate_generations().genes
