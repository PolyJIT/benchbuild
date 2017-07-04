"""This module provides unit tests for the module hill_climber.py."""
import unittest

import hill_climber


class ClimberTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pass_space = ['a', 'b']
        cls.seq_to_fitness = {"['a', 'a']": 4, "['a', 'b']": 3,
                              "['b', 'a']": 2, "['b', 'b']": 1}

    def test_sequence_functionality(self):
        sequence = ['a', 'a']
        hill_climber.calculate_fitness_value(sequence, self.seq_to_fitness,
                                             str(sequence), 'test')
        neighbours = [['a', 'b'], ['b', 'a']]
        calc_neighbours = hill_climber.calculate_neighbours(sequence,
                                                            self.seq_to_fitness,
                                                            self.pass_space,
                                                            'test')

        result = True
        for neighbour in neighbours:
            result &= neighbour in calc_neighbours

        self.assertTrue(result)

    def test_climb(self):
        sequence = hill_climber.climb(['a', 'a'], 'test', self.pass_space,
                                      self.seq_to_fitness)
        self.assertTrue(sequence == ['b', 'b'])


if __name__ == '__main__':
    unittest.main()
