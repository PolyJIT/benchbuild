#!/usr/bin/evn python2

from setuptools import setup, find_packages
setup(name='pprof',
      version='0.2',
      packages=['pprof', 'pprof.experiments'],
      author = "Andreas Simbuerger",
      author_email = "simbuerg@fim.uni-passau.de",
      description = "This is the experiment driver for the pprof study",
      license = "MIT",

      entry_points={
          'console_scripts': [ 'pprof=pprof.pprof:main' ]
          }
      )
