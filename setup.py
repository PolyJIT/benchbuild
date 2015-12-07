#!/usr/bin/env python3
from setuptools import setup, find_packages
setup(
    name='pprof',
    version='1.0',
    url='https://github.com/simbuerg/pprof-study',
    packages=find_packages(exclude=["docs", "extern", "filters", "linker",
                                    "src", "statistics", "tests", "results"]),
    install_requires=
    ["lazy==1.2", "SQLAlchemy==1.0.4", "dill==0.2.4", "plumbum>=1.5.0",
     "regex==2015.5.28", "wheel==0.24.0", "parse==1.6.6", "virtualenv==13.1.0",
     "sphinxcontrib-napoleon", "psycopg2", "sqlalchemy-migrate"],
    author="Andreas Simbuerger",
    author_email="simbuerg@fim.uni-passau.de",
    description="This is the experiment driver for the pprof study",
    license="MIT",
    entry_points={
        'console_scripts': ['pprof=pprof.driver:main']
    },
    classifiers=[
        'Development Status :: 4 - Beta', 'Intended Audience :: Developers',
        'Topic :: Software Development :: Experimentation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords="polyjit pprof experiments run-time", )
