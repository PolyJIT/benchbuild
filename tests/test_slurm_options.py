"""
Test the SLURM options generator.
"""
import unittest

import benchbuild.utils.slurm_options as sopt


class TestSlurmOptions(unittest.TestCase):
    """
    Checks base slurm options methods.
    """
    def test_script(self):
        """
        Checks that the correct sbatch option get's generated.
        """
        option = sopt.SlurmExclusive()

        self.assertEqual(option.to_slurm_opt(), "#SBATCH --exclusive")


class TestCoresPerSocket(unittest.TestCase):
    """
    Checks if the CoresPerSocket option works correctly.
    """
    def test_init_cores(self):
        """
        Checks that we can correctly initialize a CoresPerSocket option.
        """
        option = sopt.SlurmCoresPerSocket(42)

        self.assertEqual(option.cores, 42)

    def test_merge_requirements(self):
        """
        Checks if cores per socket options are correctly merged together.
        """
        option = sopt.SlurmCoresPerSocket(4)
        other_option = sopt.SlurmCoresPerSocket(8)

        merged_option = sopt.SlurmCoresPerSocket.merge_requirements(
            option, other_option)
        merged_option_swapped = sopt.SlurmCoresPerSocket.merge_requirements(
            other_option, option)

        self.assertEqual(merged_option.cores, 8)
        self.assertEqual(merged_option_swapped.cores, 8)

    def test_cli_opt(self):
        """
        Checks that the correct slurm cli option is generated.
        """
        option = sopt.SlurmCoresPerSocket(4)

        self.assertEqual(option.to_slurm_cli_opt(), "--cores-per-socket=4")


class TestExclusive(unittest.TestCase):
    """
    Checks if the CoresPerSocket option works correctly.
    """
    def test_cli_opt(self):
        """
        Checks that the correct slurm cli option is generated.
        """
        option = sopt.SlurmExclusive()

        self.assertEqual(option.to_slurm_cli_opt(), "--exclusive")


class TestNiceness(unittest.TestCase):
    """
    Checks if the Niceness option works correctly.
    """
    def test_init_niceness(self):
        """
        Checks that we can correctly initialize a Niceness option.
        """
        option = sopt.SlurmNiceness(42)

        self.assertEqual(option.niceness, 42)

    def test_merge_requirements(self):
        """
        Checks if niceness options are correctly merged together.
        """
        option = sopt.SlurmNiceness(4)
        other_option = sopt.SlurmNiceness(8)

        merged_option = sopt.SlurmNiceness.merge_requirements(
            option, other_option)
        merged_option_swapped = sopt.SlurmNiceness.merge_requirements(
            other_option, option)

        self.assertEqual(merged_option.niceness, 4)
        self.assertEqual(merged_option_swapped.niceness, 4)

    def test_cli_opt(self):
        """
        Checks that the correct slurm cli option is generated.
        """
        option = sopt.SlurmNiceness(42)

        self.assertEqual(option.to_slurm_cli_opt(), "--nice=42")


class TestHint(unittest.TestCase):
    """
    Checks if the Hint option works correctly.
    """
    def test_init_hint(self):
        """
        Checks that we can correctly initialize a Hint option.
        """
        option = sopt.SlurmHint({sopt.SlurmHint.SlurmHints.compute_bound})

        self.assertSetEqual(option.hints,
                            {sopt.SlurmHint.SlurmHints.compute_bound})

    def test_merge_requirements_disj(self):
        """
        Checks if hint options are correctly merged together.
        """
        option = sopt.SlurmHint({sopt.SlurmHint.SlurmHints.compute_bound})
        other_option = sopt.SlurmHint({sopt.SlurmHint.SlurmHints.multithread})

        merged_option = sopt.SlurmHint.merge_requirements(option, other_option)
        merged_option_swapped = sopt.SlurmHint.merge_requirements(
            other_option, option)

        self.assertSetEqual(
            merged_option.hints, {
                sopt.SlurmHint.SlurmHints.compute_bound,
                sopt.SlurmHint.SlurmHints.multithread
            })
        self.assertSetEqual(
            merged_option_swapped.hints, {
                sopt.SlurmHint.SlurmHints.compute_bound,
                sopt.SlurmHint.SlurmHints.multithread
            })

    def test_merge_requirements_additional(self):
        """
        Checks if hint options are correctly merged together.
        """
        option = sopt.SlurmHint({sopt.SlurmHint.SlurmHints.compute_bound})
        other_option = sopt.SlurmHint({
            sopt.SlurmHint.SlurmHints.multithread,
            sopt.SlurmHint.SlurmHints.compute_bound
        })

        merged_option = sopt.SlurmHint.merge_requirements(option, other_option)
        merged_option_swapped = sopt.SlurmHint.merge_requirements(
            other_option, option)

        self.assertSetEqual(
            merged_option.hints, {
                sopt.SlurmHint.SlurmHints.compute_bound,
                sopt.SlurmHint.SlurmHints.multithread
            })
        self.assertSetEqual(
            merged_option_swapped.hints, {
                sopt.SlurmHint.SlurmHints.compute_bound,
                sopt.SlurmHint.SlurmHints.multithread
            })

    def test_merge_requirements_mutally_exclusive(self):
        """
        Checks if hint options are correctly merged together.
        """
        option = sopt.SlurmHint({sopt.SlurmHint.SlurmHints.compute_bound})
        other_option = sopt.SlurmHint({sopt.SlurmHint.SlurmHints.memory_bound})

        self.assertRaises(ValueError, sopt.SlurmHint.merge_requirements,
                          option, other_option)

    def test_cli_opt(self):
        """
        Checks that the correct slurm cli option is generated.
        """
        option = sopt.SlurmHint({sopt.SlurmHint.SlurmHints.compute_bound})

        self.assertEqual(option.to_slurm_cli_opt(), "--hint=compute_bound")

    def test_cli_opt_multiple(self):
        """
        Checks that the correct slurm cli option is generated.
        """
        option = sopt.SlurmHint({
            sopt.SlurmHint.SlurmHints.compute_bound,
            sopt.SlurmHint.SlurmHints.nomultithread
        })

        output_string = option.to_slurm_cli_opt()
        self.assertTrue(output_string.startswith("--hint="))
        self.assertTrue("compute_bound" in output_string)
        self.assertTrue("nomultithread" in output_string)


class TestTime(unittest.TestCase):
    """
    Checks if the Time option works correctly.
    """
    def test_init_niceness(self):
        """
        Checks that we can correctly initialize a Time option.
        """
        option = sopt.SlurmTime("6:3:1")

        self.assertEqual(option.timelimit, (0, 6, 3, 1))

    def test_merge_requirements(self):
        """
        Checks if timelimit options are correctly merged together.
        """
        option = sopt.SlurmTime("6:3:1")
        other_option = sopt.SlurmTime("3:3:1")

        merged_option = sopt.SlurmTime.merge_requirements(option, other_option)
        merged_option_swapped = sopt.SlurmTime.merge_requirements(
            other_option, option)

        self.assertEqual(merged_option.timelimit, (0, 3, 3, 1))
        self.assertEqual(merged_option_swapped.timelimit, (0, 3, 3, 1))

    def test_cli_opt(self):
        """
        Checks that the correct slurm cli option is generated.
        """
        option = sopt.SlurmTime("6:3:1")

        self.assertEqual(option.to_slurm_cli_opt(), "--time=6:03:01")

    def test_to_slurm_time_format_minute(self):
        """
        Checks that Time correctly generates slurm time specifiers.
        """
        option = sopt.SlurmTime("1")

        self.assertEqual(option.to_slurm_time_format(), "1")

    def test_to_slurm_time_format_min_secs(self):
        """
        Checks that Time correctly generates slurm time specifiers.
        """
        option = sopt.SlurmTime("1:2")

        self.assertEqual(option.to_slurm_time_format(), "1:02")

    def test_to_slurm_time_format_hours_min_secs(self):
        """
        Checks that Time correctly generates slurm time specifiers.
        """
        option = sopt.SlurmTime("4:1:2")

        self.assertEqual(option.to_slurm_time_format(), "4:01:02")

    def test_to_slurm_time_format_days_hours(self):
        """
        Checks that Time correctly generates slurm time specifiers.
        """
        option = sopt.SlurmTime("30-10")

        self.assertEqual(option.to_slurm_time_format(), "30-10")

    def test_to_slurm_time_format_days_hours_minutes(self):
        """
        Checks that Time correctly generates slurm time specifiers.
        """
        option = sopt.SlurmTime("30-10:8")

        self.assertEqual(option.to_slurm_time_format(), "30-10:08")

    def test_to_slurm_time_format_days_hours_minutes_secs(self):
        """
        Checks that Time correctly generates slurm time specifiers.
        """
        option = sopt.SlurmTime("30-10:8:2")

        self.assertEqual(option.to_slurm_time_format(), "30-10:08:02")


class TestSlurmOptionMerger(unittest.TestCase):
    """
    Checks if slurm option list get merged correctly.
    """
    def test_merge_same(self):
        """
        Checks that merging two lists with the same option merges the options.
        """
        opt_list_1 = [sopt.SlurmCoresPerSocket(4)]
        opt_list_2 = [sopt.SlurmCoresPerSocket(8)]

        merged_list = sopt.merge_slurm_options(opt_list_1, opt_list_2)

        self.assertEqual(len(merged_list), 1)
        self.assertEqual(type(merged_list[0]), sopt.SlurmCoresPerSocket)
        self.assertEqual(merged_list[0].cores, 8)
