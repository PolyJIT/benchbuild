#!/usr/bin/env python3
from setuptools import setup, find_packages

extra_files = [
    "templates/compiler.py.inc",
    "templates/run_static.py.inc",
    "templates/run_dynamic.py.inc",
    "templates/slurm.sh.inc"
]

src_extra_files = [
    "patches/linpack.patch"
]

sql_extra_files = [
    "func.compare_region_wise2.sql",
    "func.experiments.sql",
    "func.recompilation.sql",
    "func.run_regions.sql",
    "func.total_dyncov_clean.sql",
    "func.total_speedup.sql",
    "func.compare_region_wise.sql",
    "func.project_region_time.sql",
    "func.run_durations.sql",
    "func.speedup.sql",
    "func.total_dyncov.sql",
    "func.pj-test-eval.sql",
    "func.compilestats_eval.sql",
    "func.polly_mse.sql",
]

setup(
    name='benchbuild',
    version='2.0.1',
    url='https://github.com/PolyJIT/benchbuild',
    packages=find_packages(exclude=["docs", "extern", "filters", "linker",
                                    "src", "statistics", "tests", "results"]),
    package_data={"benchbuild.utils": extra_files,
                  "benchbuild": sql_extra_files,
                  "becnbuild.projects": src_extra_files},
    include_package_data=True,
    install_requires=[
        "dill>=0.2",
        "SQLAlchemy>=1.0",
        "plumbum>=1.5",
        "regex>=2015",
        "parse>=1.6",
        "virtualenv>=13.1",
        "psycopg2>=2.7",
        "sqlalchemy-migrate",
        "pandas>=0.20.3",
        "psutil>=4.0.0",
        "PyYAML>=3.12",
        "Jinja2>=2.2"
    ],
    author="Andreas Simbuerger",
    author_email="simbuerg@fim.uni-passau.de",
    description="This is the experiment driver for the benchbuild study",
    license="MIT",
    entry_points={
        'console_scripts': ['benchbuild=benchbuild.driver:main',
                            'container=benchbuild.container:main']
    },
    classifiers=[
        'Development Status :: 4 - Beta', 'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords="benchbuild experiments run-time", )
