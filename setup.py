#!/usr/bin/evn python2

from setuptools import setup, find_packages
setup(name='pprof',
      version='0.8.4',
      packages= find_packages(),
      setup_requires=['plumbum', 'cloud', 'psycopg2', 'virtualenv', 'regex'],
      author = "Andreas Simbuerger",
      author_email = "simbuerg@fim.uni-passau.de",
      description = "This is the experiment driver for the pprof study",
      license = "MIT",
      entry_points={
          'console_scripts': [ 'pprof=pprof.driver:main' ]
          }
      )
