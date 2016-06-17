#!/usr/bin/env python3
from setuptools import setup, find_packages
setup(
    name='benchbuild',
    version='1.1',
    url='https://github.com/simbuerg/benchbuild',
    packages=find_packages(exclude=["docs", "extern", "filters", "linker",
                                    "src", "statistics", "tests", "results"]),
    install_requires=
    ["lazy==1.2", "SQLAlchemy==1.0.4", "dill==0.2.4", "plumbum>=1.5.0",
     "regex==2015.5.28", "wheel==0.24.0", "parse==1.6.6", "virtualenv==13.1.0",
     "sphinxcontrib-napoleon", "psycopg2", "sqlalchemy-migrate", "six>=1.7.0",
     "psutil>=4.0.0", "pylint>=1.5.5"],
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
