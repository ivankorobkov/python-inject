# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'inject'
author = 'Ivan Korobkov'
copyright = '2010-%Y, ' + author

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
#     'sphinx.ext.duration',
#     'sphinx.ext.todo',           # Support for todo items
    'sphinx.ext.viewcode',       # Add links to highlighted source code
#     'sphinx.ext.intersphinx',    # Link to other projects’ documentation
#     # custom extentions
    'sphinx_rtd_theme',
    'sphinx_copybutton',         # add a little “copy” button to the right of your code blocks
#     'sphinx_design',             # for designing beautiful, screen-size responsive web-components
#     'sphinx_favicon',
#     'sphinx_togglebutton',
#     # not used
    'sphinx.ext.autodoc',      # Include documentation from docstrings  # check sphinx.ext.apidoc
#     'sphinx.ext.napoleon',     # Support for NumPy and Google style docstrings
#     # 'sphinx.ext.autosummary',  # Generate autodoc summaries
#     # 'sphinx.ext.graphviz',     # Add Graphviz graphs
]

autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
