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

setup(
    name='benchbuild',
    use_scm_version=True,
    url='https://github.com/PolyJIT/benchbuild',
    packages=find_packages(
        exclude=[
            "docs", "extern", "filters", "linker", "src", "statistics", "tests",
            "results"
        ]
    ),
    package_data={"benchbuild": RESOURCES},
    include_package_data=True,
    setup_requires=["pytest-runner", "setuptools_scm"],
    install_requires=[
        "Jinja2~=3.1", "PyYAML~=6.0", "attrs~=22.2", "dill==0.3.4",
        "pathos~=0.2", "parse~=1.19", "plumbum~=1.8", "psutil~=5.9",
        "psycopg2-binary~=2.9", "pygit2~=1.11", "pygtrie~=2.5",
        "pyparsing~=3.0", "rich~=13.3", "SQLAlchemy<2",
        "sqlalchemy-migrate~=0.13", "typing-extensions~=4.4",
        "virtualenv~=20.19", "schema~=0.7", "result~=0.9"
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
    keywords="benchbuild experiments run-time"
)
