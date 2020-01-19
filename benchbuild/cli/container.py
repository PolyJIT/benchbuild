"""Subcommand for containerizing benchbuild experiments."""
import itertools
from typing import Generator, List, Tuple

from plumbum import cli

from benchbuild import environments, experiment, plugins, project, source
from benchbuild.cli.main import BenchBuild
from benchbuild.environments import Buildah
from benchbuild.utils.cmd import mkdir, rm


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

        # For all project versions:
        # 2. Build project image.
        final_images = []
        for p_name, p_image in build_project_images(wanted_experiments,
                                                    wanted_projects):
            # 3. Build experiment image from each project image.
            for e_image in build_experiment_images(p_name, p_image,
                                                   wanted_experiments):
                # 4. Integrate bencbuild into the experiment image
                final_images.append(add_benchbuild(e_image))

        # 5. Prepare results directory
        # 6. Setup podman container.
        # 7. Call benchbuild run with the given experiment/project config.


def build_project_images(
        wanted_experiments,
        wanted_projects) -> Generator[Tuple[str, str], None, None]:
    """Build container images."""
    combinations = itertools.product(wanted_projects.items(),
                                     wanted_experiments.items())

    def build_project_image(prj: project.Project) -> Buildah:
        # Setup build context
        builddir = prj.builddir

        mkdir('-p', builddir)
        container = prj.container

        variant = prj.variant
        for version in variant.values():
            src = version.owner
            loc = src.version(builddir, str(version))
            container.add(loc, f"/.benchuild/{version}")

        container = environments.finalize_project_container(prj, container)
        rm('-r', builddir)
        return container

    for (prj_key, prj_cls), (_, exp_cls) in combinations:
        # FIXME: Need customizable version filters
        for variant in source.product(prj_cls.SOURCE):
            ctx = source.variants.context(variant)
            if not hasattr(prj_cls, 'CONTAINER'):
                print(f"{prj_key} does not support container mode yet.")
                continue
            exp = exp_cls()
            prj: project.Project = prj_cls(exp, variant=ctx)

            for image_info in environments.by_project(prj):
                yield (prj_key, image_info["id"])
                break
            else:
                # FIXME: Support forced rebuild.
                print(f"Building... {str(ctx)}")
                yield (prj_key, build_project_image(prj))


def build_experiment_images(name: str, image: str,
                            wanted_experiments) -> Generator[str, None, None]:
    for exp, _ in wanted_experiments.items():
        tag = f"{exp}/{name}:{image[:12]}"
        for image_info in environments.by_tag(tag):
            container = image_info["id"]
            yield tag
            break
        else:
            container = Buildah()
            container.from_(image)
            yield container.finalize(tag)


def add_benchbuild(image: str) -> str:

    def from_source():
        pass

    def from_pip():
        pass

    src_dir = '/home/simbuerg/src/polyjit/benchbuild'
    tgt_dir = '/benchbuild'

    container = Buildah().from_(image)
    container.run('/bin/mkdir', '/benchbuild', runtime='/usr/bin/crun')
    container.run('/usr/bin/pip',
                  'install',
                  '/benchbuild/',
                  mount=f'type=bind,src={src_dir},target={tgt_dir}',
                  runtime='/usr/bin/crun')
    return container.finalize(tag=f'{image}-bb')
