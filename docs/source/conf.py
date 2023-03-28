# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import logging
import os

from pkg_resources import DistributionNotFound, get_distribution

import benchbuild.utils

# pylint: skip-file
try:
    __version__ = get_distribution("benchbuild").version
except DistributionNotFound:
    pass

project = 'BenchBuild'
copyright = '2023, Andreas Simbürger'
author = 'Andreas Simbürger'
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
    'sphinxcontrib.programoutput',
    'sphinx.ext.githubpages',
]

myst_gfm_only = True
myst_enable_extensions = ["linkify"]

# templates_path = ['_templates']
exclude_patterns = []

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
