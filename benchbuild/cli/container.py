"""Subcommand for containerizing benchbuild experiments."""
from typing import List

from plumbum import cli

from benchbuild import plugins, environments, experiment, project, source
from benchbuild.cli.main import BenchBuild


@BenchBuild.subcommand("container")
class BenchBuildContainer(cli.Application):
    experiment_args: List[str] = []
    group_args: List[str] = []

    @cli.switch(["-E", "--experiment"],
                str,
                list=True,
                help="Specify experiments to run")
    def set_experiments(self, names):
        self.experiment_args = names

    @cli.switch(["-G", "--group"],
                str,
                list=True,
                requires=["--experiment"],
                help="Run a group of projects under the given experiments")
    def set_group(self, groups):
        self.group_args = groups

    pretend = cli.Flag(['p', 'pretend'], default=False)
    """Frontend for running experiments inside a containerized environment."""
    def main(self, *projects):
        """Main entry point of benchbuild container."""
        plugins.discover()
        cli_experiments = self.experiment_args
        cli_groups = self.group_args

        # 1. Select Projects/Experiments
        discovered_experiments = experiment.discovered()
        wanted_experiments = dict(
            filter(lambda pair: pair[0] in set(cli_experiments),
                   discovered_experiments.items()))
        unknown_experiments = list(
            filter(lambda name: name not in discovered_experiments.keys(),
                   set(cli_experiments)))

        if unknown_experiments:
            print('Could not find ', str(unknown_experiments),
                  ' in the experiment registry.')
        if not wanted_experiments:
            print("Could not find any experiment. Exiting.")
            return -2

        wanted_projects = project.populate(projects, cli_groups)
        if not wanted_projects:
            print("No projects selected.")
            return -2

        build_images(wanted_experiments, wanted_projects)
        # For all project versions:
        # 2. Build project image.
        # 3. Build experiment image from each project image.

        # 4. Integrate bencbuild into the experiment image

        # 5. Prepare results directory
        # 6. Setup podman container.
        # 7. Call benchbuild run with the given experiment/project config.


def build_images(wanted_experiments, wanted_projects) -> List[str]:
    """Build container images."""
    images = []
    for prj_key, prj_cls in wanted_projects.items():
        prj_variants = source.product(prj_cls.SOURCE)
        for variant in prj_variants:
            ctx = source.variants.context(variant)
            if not hasattr(prj_cls, 'CONTAINER'):
                print(f"{prj_key} does not support container mode yet.")
                continue

            for _, exp_cls in wanted_experiments.items():
                exp = exp_cls()
                prj = prj_cls(exp, variant=ctx)

                for image_info in environments.by_project(prj):
                    container = image_info["id"]
                    images.append(container)
                    break
                else:
                    # FIXME: Support container per version.
                    # FIXME: Support forced rebuild.
                    container = prj_cls.CONTAINER
                    container = environments.finalize_project_container(
                        prj, container)

    print(images)
