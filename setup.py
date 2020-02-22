from setuptools import find_namespace_packages, setup

with open('README.md') as f:
    long_description = f.read()

extra_files = [
    "templates/run_compiler.py.inc", "templates/run_static.py.inc",
    "templates/run_dynamic.py.inc", "templates/slurm.sh.inc"
]

src_extra_files = ["patches/linpack.patch"]

sql_extra_files = [
    "func.compare_region_wise2.sql", "func.experiments.sql",
    "func.recompilation.sql", "func.run_regions.sql",
    "func.total_dyncov_clean.sql", "func.total_speedup.sql",
    "func.compare_region_wise.sql", "func.project_region_time.sql",
    "func.run_durations.sql", "func.speedup.sql", "func.total_dyncov.sql",
    "func.pj-test-eval.sql", "func.compilestats_eval.sql", "func.polly_mse.sql",
    "func.profileScopDetection-eval.sql"
]

setup(name='benchbuild',
      use_scm_version=True,
      url='https://github.com/PolyJIT/benchbuild',
      packages=find_namespace_packages(include=['benchbuild', 'benchbuild.*']),
      package_data={
          "benchbuild.utils": extra_files,
          "benchbuild": sql_extra_files,
          "becnbuild.projects": src_extra_files
      },
      include_package_data=True,
      setup_requires=["pytest-runner", "setuptools_scm"],
      tests_require=["pytest"],
      install_requires=[
          "attrs>=17.4.0",
          "coloredlogs~=10.0",
          "defer>=1.0",
          "dill>=0.2",
          "Jinja2>=2.2",
          "pandas>=0.20.3",
          "parse>=1.6",
          "plumbum>=1.5",
          "psutil>=4.0.0",
          "psycopg2-binary>=2.7",
          "pygtrie>=2.2",
          "pyparsing>=2.2",
          "PyYAML~=5.1",
          "sqlalchemy-migrate",
          "SQLAlchemy>=1.0",
          "virtualenv>=13.1",
      ],
      author="Andreas Simbuerger",
      author_email="simbuerg@fim.uni-passau.de",
      description="This is the experiment driver for the benchbuild study",
      long_description=long_description,
      long_description_content_type='text/markdown',
      license="MIT",
      entry_points={'console_scripts': ['benchbuild=benchbuild.cli:__main__']},
      classifiers=[
          'Development Status :: 4 - Beta', 'Intended Audience :: Developers',
          'Topic :: Software Development :: Testing',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3'
      ],
      keywords="benchbuild experiments run-time")
