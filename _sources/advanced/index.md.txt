# SLURM

BenchBuild supports a high-level integration with the SLURM cluster resource
manager. An experiment setup can be exported as a SLURM bash script. Assuming
you have access to a configured benchbuid environment on the SLURM cluster, you
can provide the SLURM script to the ``sbatch`` command and have your experiment
run on the cluster environment.

## Basics

TODO

## Template customization

This customization is not recommended for the default use-case. However, you
might run in a situation where the existing cluster-environment requires a
more complicated setup than BenchBuild can provide.

You can customize the template that is used for the SLURM script using a
modified copy of the base template BenchBuild uses
(see ``benchbuild/res/misc/slurm.sh.inc``).

The customized template can be configured using the configuration option
``BB_SLURM_TEMPLATE``. If BenchBuild detects that the provided value points to
an existing file in your filesystem, it will load it.
If you change the setting and BenchBuild cannot find a file there, no script
will be generated. No validation of the template will be done, use at your own
risk.
