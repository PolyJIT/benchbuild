"""This module provides unit tests for the module genetic1.py."""
import unittest

import genetic1


class ChromosomeTestCase(unittest.TestCase):
    def setUp(self):
        self.gene_sequences = [['a', 'a', 'a'], ['b', 'b', 'b'],
                               ['c', 'c', 'c']]
        genetic1.seq_to_fitness = {'aaa': 1, 'bbb': 2, 'ccc': 3}

    def test_chromosome_fitness_calculation(self):
        for genes in self.gene_sequences:
            chromosome = genetic1.Chromosome(genes, 'test')
            chromosome.calculate_fitness_value()
            key = ''.join(genes)
            self.assertTrue(
                chromosome.fitness_value == genetic1.seq_to_fitness[key])

    def test_chromosome_equals_method(self):
        a = genetic1.Chromosome(self.gene_sequences[0], 'test')
        b = genetic1.Chromosome(self.gene_sequences[0], 'test')
        c = genetic1.Chromosome(self.gene_sequences[0], 'not_test')
        d = genetic1.Chromosome(self.gene_sequences[1], 'test')
        e = genetic1.Chromosome(self.gene_sequences[1], 'not_test')
        self.assertTrue(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == d)
        self.assertFalse(a == e)


class PopulationTestCase(unittest.TestCase):
    def setUp(self):
        self.gene_pool = ['a']
        self.population = genetic1.Population('test', size=4,
                                              gene_pool=self.gene_pool,
                                              chromosome_size=2)

    def test_population_creation(self):
        size1 = 4
        chromosome_size1 = -1
        gene_pool1 = []
        population1 = genetic1.Population('test', size1, gene_pool1,
                                          chromosome_size1)
        self.assertTrue(population1.size == genetic1.MIN_POPULATION_SIZE)
        self.assertTrue(population1.gene_pool == genetic1.DEFAULT_GENE_POOL)
        self.assertTrue(population1.chromosome_size == 0)
        for chromosome in population1.chromosomes:
            self.assertTrue(len(chromosome.genes) == 0)

        size2 = 11
        chromosome_size2 = 4
        gene_pool2 = ['a', 'b']
        population2 = genetic1.Population('test', size2, gene_pool2,
                                          chromosome_size2)
        self.assertTrue(population2.size == size2)
        self.assertFalse(population2.gene_pool == genetic1.DEFAULT_GENE_POOL)
        self.assertTrue(population2.chromosome_size == chromosome_size2)
        for chromosome in population2.chromosomes:
            self.assertTrue(len(chromosome.genes) == chromosome_size2)

    def test_simulate_generation(self):
        env = 'test'
        size = 10
        gene_pool = ['a', 'b']
        chromosome_size = 2
        genetic1.seq_to_fitness = {'aa': 4, 'ab': 3, 'ba': 2, 'bb': 1}
        population = genetic1.Population(env, size, gene_pool, chromosome_size)

        chromosomes = [genetic1.Chromosome(['a', 'a'], env),
                       genetic1.Chromosome(['a', 'b'], env),
                       genetic1.Chromosome(['a', 'b'], env),
                       genetic1.Chromosome(['b', 'a'], env),
                       genetic1.Chromosome(['b', 'a'], env),
                       genetic1.Chromosome(['b', 'a'], env),
                       genetic1.Chromosome(['b', 'b'], env),
                       genetic1.Chromosome(['b', 'b'], env),
                       genetic1.Chromosome(['b', 'b'], env),
                       genetic1.Chromosome(['b', 'b'], env)]
        population.chromosomes = chromosomes
        population.simulate_generations(1)

        self.assertTrue(
            population.fittest_chromosome == genetic1.Chromosome(['b', 'b'],
                                                                 env))


if __name__ == '__main__':
    unittest.main()