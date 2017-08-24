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
    "func.compilestats_eval.sql"
]

setup(
    name='benchbuild',
    version='1.3.2',
    url='https://github.com/PolyJIT/benchbuild',
    packages=find_packages(exclude=["docs", "extern", "filters", "linker",
                                    "src", "statistics", "tests", "results"]),
    package_data={"benchbuild.utils": extra_files,
                  "benchbuild": sql_extra_files,
                  "becnbuild.projects": src_extra_files},
    include_package_data=True,
    install_requires=[
        "SQLAlchemy==1.0.4",
        "dill==0.2.6",
        "plumbum>=1.5.0",
        "regex==2015.5.28",
        "wheel==0.24.0",
        "parse==1.6.6",
        "virtualenv==13.1.0",
        "sphinxcontrib-napoleon",
        "psycopg2",
        "sqlalchemy-migrate",
        "six>=1.7.0",
        "pandas>=0.20.3",
        "psutil>=4.0.0",
        "pylint>=1.5.5",
        "PyYAML>=3.12",
        "Jinja2>=2.2",
        "numpy>=1.8.2",
        "scipy==0.19.1",
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
