#!/usr/bin/evn python2

from setuptools import setup, find_packages
setup(name='pprof',
      version='0.9.6',
      packages=find_packages(),
      install_requires=["SQLAlchemy==1.0.4", "cloud==2.8.5", "plumbum==1.4.2",
                        "regex==2015.5.28", "wheel==0.24.0", "parse==1.6.6"],
      author="Andreas Simbuerger",
      author_email="simbuerg@fim.uni-passau.de",
      description="This is the experiment driver for the pprof study",
      license="MIT",
      entry_points={
          'console_scripts': ['pprof=pprof.driver:main']
      }
)
