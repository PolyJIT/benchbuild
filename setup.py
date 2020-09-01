from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

RESOURCES = [
    'res/misc/slurm.sh.inc', "res/sql/func.compare_region_wise2.sql",
    "res/sql/func.experiments.sql", "res/sql/func.recompilation.sql",
    "res/sql/func.run_regions.sql", "res/sql/func.total_dyncov_clean.sql",
    "res/sql/func.total_speedup.sql", "res/sql/func.compare_region_wise.sql",
    "res/sql/func.project_region_time.sql", "res/sql/func.run_durations.sql",
    "res/sql/func.speedup.sql", "res/sql/func.total_dyncov.sql",
    "res/sql/func.pj-test-eval.sql", "res/sql/func.compilestats_eval.sql",
    "res/sql/func.polly_mse.sql", "res/sql/func.profileScopDetection-eval.sql",
    "res/wrapping/run_compiler.py.inc", "res/wrapping/run_static.py.inc",
    "res/wrapping/run_dynamic.py.inc", "res/patches/linpack.patch"
]

setup(name='benchbuild',
      use_scm_version=True,
      url='https://github.com/PolyJIT/benchbuild',
      packages=find_packages(exclude=[
          "docs", "extern", "filters", "linker", "src", "statistics", "tests",
          "results"
      ]),
      package_data={"benchbuild": RESOURCES},
      include_package_data=True,
      setup_requires=["pytest-runner", "setuptools_scm"],
      tests_require=["pytest", "pytest-describe"],
      install_requires=[
          "Jinja2~=2.10", "PyYAML~=5.1", "attrs~=19.3", "dill~=0.3",
          "pandas>=0.25,<2.0", "pathos~=0.2", "parse~=1.14", "pdoc3~=0.8",
          "plumbum~=1.6", "psutil~=5.6", "psycopg2-binary~=2.8", "pygtrie~=2.3",
          "pyparsing~=2.4", "sqlalchemy-migrate~=0.13", "virtualenv>=16.7,<21.0"
      ],
      author="Andreas Simbuerger",
      author_email="simbuerg@fim.uni-passau.de",
      description="This is the experiment driver for the benchbuild study",
      long_description=long_description,
      long_description_content_type='text/markdown',
      license="MIT",
      entry_points={
          'console_scripts': [
              'benchbuild=benchbuild.driver:main',
              'container=benchbuild.container:main'
          ]
      },
      classifiers=[
          'Development Status :: 4 - Beta', 'Intended Audience :: Developers',
          'Topic :: Software Development :: Testing',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3'
      ],
      keywords="benchbuild experiments run-time")
