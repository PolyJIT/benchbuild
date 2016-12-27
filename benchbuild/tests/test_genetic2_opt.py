"""This module provides unit tests for the module genetic2_opt.py."""
import unittest

import genetic2_opt


class PopulationTestCase(unittest.TestCase):
    def test_simulate_generation(self):
        env = 'test'
        gene_pool = ['a', 'b']
        seq_to_fitness = {"['a', 'a']": 4, "['a', 'b']": 3, "['b', 'a']": 2,
                          "['b', 'b']": 1}

        chromosomes = [['a', 'a'], ['a', 'b'], ['a', 'b'], ['b', 'a'],
                       ['b', 'a'], ['b', 'a'], ['b', 'b'], ['b', 'b'],
                       ['b', 'b'], ['b', 'b']]

        result, fittest = genetic2_opt.simulate_generation(chromosomes,
                                                           gene_pool, env,
                                                           seq_to_fitness)

        self.assertTrue(fittest == ['b', 'b'])


if __name__ == '__main__':
    unittest.main()