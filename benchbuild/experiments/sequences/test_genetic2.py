"""This module provides unit tests for the module genetic2.py."""
import unittest

import genetic2


class ChromosomeTestCase(unittest.TestCase):
    def setUp(self):
        self.gene_sequences = [['a', 'a', 'a'], ['b', 'b', 'b'],
                               ['c', 'c', 'c']]
        self.seq_to_fitness = {"['a', 'a', 'a']": 1, "['b', 'b', 'b']": 2,
                               "['c', 'c', 'c']": 3}

    def test_chromosome_fitness_calculation(self):
        for genes in self.gene_sequences:
            chromosome = genetic2.Chromosome(genes, 'test')
            chromosome.calculate_fitness_value(self.seq_to_fitness)
            key = str(genes)
            self.assertTrue(
                chromosome.fitness_value == self.seq_to_fitness[key])

    def test_chromosome_equals_method(self):
        a = genetic2.Chromosome(self.gene_sequences[0], 'test')
        b = genetic2.Chromosome(self.gene_sequences[0], 'test')
        c = genetic2.Chromosome(self.gene_sequences[0], 'not_test')
        d = genetic2.Chromosome(self.gene_sequences[1], 'test')
        e = genetic2.Chromosome(self.gene_sequences[1], 'not_test')
        self.assertTrue(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == d)
        self.assertFalse(a == e)


class PopulationTestCase(unittest.TestCase):
    def setUp(self):
        self.gene_pool = ['a']
        self.population = genetic2.Population('test', size=4,
                                              gene_pool=self.gene_pool,
                                              chromosome_size=2)

    def test_population_creation(self):
        size1 = 4
        chromosome_size1 = -1
        gene_pool1 = []
        population1 = genetic2.Population('test', size1, gene_pool1,
                                          chromosome_size1)
        self.assertTrue(population1.size == genetic2.MIN_POPULATION_SIZE)
        self.assertTrue(population1.gene_pool == genetic2.DEFAULT_GENE_POOL)
        self.assertTrue(population1.chromosome_size == 0)
        for chromosome in population1.chromosomes:
            self.assertTrue(len(chromosome.genes) == 0)

        size2 = 11
        chromosome_size2 = 4
        gene_pool2 = ['a', 'b']
        population2 = genetic2.Population('test', size2, gene_pool2,
                                          chromosome_size2)
        self.assertTrue(population2.size == size2)
        self.assertFalse(population2.gene_pool == genetic2.DEFAULT_GENE_POOL)
        self.assertTrue(population2.chromosome_size == chromosome_size2)
        for chromosome in population2.chromosomes:
            self.assertTrue(len(chromosome.genes) == chromosome_size2)

    def test_simulate_generation(self):
        env = 'test'
        size = 10
        gene_pool = ['a', 'b']
        chromosome_size = 2
        seq_to_fitness = {"['a', 'a']": 4, "['a', 'b']": 3, "['b', 'a']": 2,
                          "['b', 'b']": 1}
        population = genetic2.Population(env, size, gene_pool, chromosome_size)

        chromosomes = [genetic2.Chromosome(['a', 'a'], env),
                       genetic2.Chromosome(['a', 'b'], env),
                       genetic2.Chromosome(['a', 'b'], env),
                       genetic2.Chromosome(['b', 'a'], env),
                       genetic2.Chromosome(['b', 'a'], env),
                       genetic2.Chromosome(['b', 'a'], env),
                       genetic2.Chromosome(['b', 'b'], env),
                       genetic2.Chromosome(['b', 'b'], env),
                       genetic2.Chromosome(['b', 'b'], env),
                       genetic2.Chromosome(['b', 'b'], env)]
        population.chromosomes = chromosomes
        population.simulate_generation(seq_to_fitness)

        self.assertTrue(
            population.fittest_chromosome == genetic2.Chromosome(['b', 'b'],
                                                                 env))


if __name__ == '__main__':
    unittest.main()