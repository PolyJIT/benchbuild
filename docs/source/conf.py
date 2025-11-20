# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import logging
import os

import importlib.metadata

import benchbuild.utils

# pylint: skip-file
__version__ = importlib.metadata.version("benchbuild")

project = "BenchBuild"
copyright = "2025, Andreas Simbürger"
author = "Andreas Simbürger"
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
    "sphinxcontrib.programoutput",
    "sphinx.ext.githubpages",
]

exclude_patterns = []

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "press"
pygments_style = "monokai"
html_static_path = ["_static"]

napoleon_google_docstring = True
napoleon_use_admonition_for_examples = True

# Configure MyST Parser
# myst_gfm_only = True
myst_enable_extensions = ["linkify"]
