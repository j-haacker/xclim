#!/usr/bin/env python
#
# xclim documentation build configuration file, created by
# sphinx-quickstart on Fri Jun  9 13:47:02 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.
from __future__ import annotations

import datetime
import json
import os
import sys
import warnings

import xarray
import yaml
from pybtex.plugin import register_plugin  # noqa
from pybtex.style.formatting.alpha import Style as AlphaStyle  # noqa
from pybtex.style.labels import BaseLabelStyle  # noqa

xarray.DataArray.__module__ = "xarray"
xarray.Dataset.__module__ = "xarray"
xarray.CFTimeIndex.__module__ = "xarray"

import xclim  # noqa
from xclim.core.indicator import registry  # noqa

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory is
# relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))

# Indicator data for populating the searchable indicators page
# Get all indicators and some information about them
indicators = {}
# FIXME: Include cf module when its indicators documentation is improved.
for module in ("atmos", "generic", "land", "seaIce", "icclim", "anuclim"):
    for key, ind in getattr(xclim.indicators, module).__dict__.items():
        if hasattr(ind, "_registry_id") and ind._registry_id in registry:  # noqa
            indicators[ind._registry_id] = {  # noqa
                "realm": ind.realm,
                "title": ind.title,
                "name": key,
                "module": module,
                "abstract": ind.abstract,
                "vars": {
                    param_name: f"{param.description}"
                    for param_name, param in ind._all_parameters.items()  # noqa
                    if param.kind < 2 and not param.injected
                },
                "keywords": ind.keywords.split(","),
            }
# Sort by title
indicators = dict(sorted(indicators.items(), key=lambda kv: kv[1]["title"]))

# Dump indicators to json. The json is added to the html output (html_extra_path)
# It is read by _static/indsearch.js to populate the table in indicators.rst
os.makedirs("_dynamic", exist_ok=True)
with open("_dynamic/indicators.json", "w") as f:
    json.dump(indicators, f)


# Dump variables information
with open("variables.json", "w") as fout:
    with open("../xclim/data/variables.yml") as fin:
        data = yaml.safe_load(fin)
    json.dump(data, fout)

# -- General configuration ---------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.coverage",
    "sphinx.ext.todo",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "rstjinja",
    "nbsphinx",
    "IPython.sphinxext.ipython_console_highlighting",
    "autodoc_indicator",
    "sphinxcontrib.bibtex",
    "sphinxcontrib.cairosvgconverter",
    # sphinx_autodoc_typehints must always be listed after sphinx.ext.napoleon
    "sphinx_autodoc_typehints",
    "sphinx_codeautolink",
    "sphinx_copybutton",
    "sphinx_mdinclude",
]

autodoc_typehints = "description"
autodoc_typehints_format = "fully-qualified"
autodoc_typehints_description_target = "documented_params"

autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 2

linkcheck_ignore = [
    # too labourious to fully check
    r"https://github.com/Ouranosinc/xclim/(pull|issue).*",
    # Added on 2022-09-22: Does not allow linkcheck requests (error 403)
    r"https://doi.org/10.1093/mnras/225.1.155",
    # Bad ssl certificate
    r"https://hal.inrae.fr/hal-02843898",
    # Added on 2022-12-05: Taylor and Francis online does not allow linkcheck requests (error 403)
    r"https://www.tandfonline.com/.*",
    r"https://doi.org/10.1080/.*",
    # Added on 2022-12-08: Site appears to be down (timeout)
    r"http://www.utci.org/.*",
    # Added on 2023-01-24: bad ssl certificate
    r"https://ui.adsabs.harvard.edu/abs/2018AGUFMIN33A..06A*",
    # Added on 2023-01-31: JSTOR does not allow linkcheck requests (error 403)
    r"https://www.jstor.org/.*",
    r"https://doi.org/10.2307/210739",
    # Added on 2023-03-02: Wiley does not allow linkcheck requests (error 403)
    r"https://onlinelibrary.wiley.com/.*",
    r"https://doi.org/(10.1002|10.1029|10.1111)/.*",
    # Added on 2023-03-02: NRC does not allow linkcheck requests (error 403)
    r"https://doi.org/10.4141/S04-019",
    r"https://doi.org/10.4141/cjps65-051",
    # Added on 2023-03-02: AGU pubs does not allow linkcheck requests (error 403)
    r"https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2008GL037119",
    # Added on 2023-03-02: Site appears to be down (error 500)
    r"https://www.semanticscholar.org/paper/A-Multivariate-Two-Sample-Test-Based-on-the-Concept-Zech-Aslan/.*",
    # Added on 2023-03-08: OGC does not allow linkcheck requests (error 403)
    r"https://www.ogc.org/standard/wps/.*",
    # Added on 2023-04-17: IEEE messes around with linkcheck requests (error 418)
    r"https://ieeexplore.ieee.org/.*",
    # Added on 2023-04-19: Site appears to be down (error 418)
    r"https://doi.org/10.1109/.*",
    r"https://ieeexplore.ieee.org/document/1544887/",
    # Added on 2023-04-19: Site appears to be down (error 404)
    r"https://doi.org/10.1214/.*"
    r"https://projecteuclid.org/journals/annals-of-statistics/volume-7/issue-4/Multivariate-Generalizations-of-the-Wald-Wolfowitz-and-Smirnov-Two-Sample/10.1214/aos/1176344722.full",
    r"https://projecteuclid.org/journals/annals-of-statistics/volume-16/issue-2/A-Multivariate-Two-Sample-Test-Based-on-the-Number-of/10.1214/aos/1176350835.full",
    # Added on 2023-05-03: Site appears to be down (error 502)
    r"https://openresearchsoftware.metajnl.com/article/10.5334/jors.122/",
    # Added on 2023-05-03: Connection refused for bots (error 104)
    r"https://doi.org/10.13031/2013.26773",
    # Added on 2023-05-03: linkcheck has issues with some anchors
    r"https://peps.python.org/pep-0537/#features-for-3-7",
    r"https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html#scipy.interpolate.griddata",
    r"https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skew.html#scipy.stats.skew",
]
linkcheck_exclude_documents = [r"readme"]

napoleon_numpy_docstring = True
napoleon_use_rtype = False
napoleon_use_param = False
napoleon_use_ivar = True

# see: https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html#unknown-target-name-when-using-footnote-citations-with-numpydoc
numpydoc_class_members_toctree = False

intersphinx_mapping = {
    "clisops": ("https://clisops.readthedocs.io/en/latest/", None),
    "flox": ("https://flox.readthedocs.io/en/latest/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "sklearn": ("https://scikit-learn.org/stable/", None),
    "statsmodels": ("https://www.statsmodels.org/stable/", None),
}
extlinks = {
    "issue": ("https://github.com/Ouranosinc/xclim/issues/%s", "GH/%s"),
    "pull": ("https://github.com/Ouranosinc/xclim/pull/%s", "PR/%s"),
    "user": ("https://github.com/%s", "@%s"),
}


# Bibliography stuff
# a simple label style which uses the bibtex keys for labels
class XCLabelStyle(BaseLabelStyle):
    def format_labels(self, sorted_entries):
        for entry in sorted_entries:
            yield entry.key


class XCStyle(AlphaStyle):
    default_label_style = XCLabelStyle


register_plugin("pybtex.style.formatting", "xcstyle", XCStyle)
bibtex_bibfiles = ["references.bib"]
bibtex_default_style = "xcstyle"
bibtex_reference_style = "author_year"

skip_notebooks = os.getenv("SKIP_NOTEBOOKS")
if skip_notebooks or os.getenv("READTHEDOCS_VERSION_TYPE") in [
    "branch",
    "external",
]:
    if skip_notebooks:
        warnings.warn("Not executing notebooks.")
    nbsphinx_execute = "never"
elif os.getenv("READTHEDOCS_VERSION_NAME") in ["latest", "stable"]:
    nbsphinx_execute = "always"
else:
    nbsphinx_execute = "auto"
nbsphinx_prolog = r"""
{% set docname = env.doc2path(env.docname, base=None) %}

.. only:: html

    `Download this notebook from github. <https://github.com/Ouranosinc/xclim/raw/main/docs/{{ docname }}>`_
"""
nbsphinx_timeout = 300
nbsphinx_allow_errors = False
# nbsphinx_requirejs_path = ""  # To make MiniSearch work in the indicators page

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# If a list of string, all suffixes will be understood as restructured text variants.
source_suffix = [".rst"]

# The root toctree document.
root_doc = "index"

# General information about the project.
project = "xclim"
copyright = (
    f"2018-{datetime.datetime.now().year}, Ouranos Inc., Travis Logan, and contributors"
)
author = "xclim Project Development Team"

# The version info for the project you're documenting, acts as replacement
# for |version| and |release|, also used in various other places throughout
# the built documents.
#
# The short X.Y version.
version = xclim.__version__.split("-")[0]
# The full version, including alpha/beta/rc tags.
release = xclim.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "notebooks/xclim_training",
    "paper/paper.md",
    "**.ipynb_checkpoints",
]

# The name of the Pygments (syntax highlighting) style to use for light and dark themes.
pygments_style = "sas"
pygments_dark_style = "lightbulb"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML output -------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_title = "xclim Official Documentation"
html_short_title = "xclim"

html_theme = "furo"
html_extra_path = ["variables.json"]

# Theme options are theme-specific and customize the look and feel of a theme further.
# For a list of options available for each theme, see the documentation.
html_theme_options = {
    "light_logo": "xclim-logo-light.png",
    "dark_logo": "xclim-logo-dark.png",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/Ouranosinc/xclim",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,  # noqa: E501
            "class": "",
        },
    ],
    
    "dark_css_variables": {
        "color-table-rows-even": "#303335",
        "color-copybutton": "#fff",
        "color-indicator-text": "#cfd0d0",
        "color-indicator-background": "#3e3e3e",
        "color-indicator-widget-text": "#a8a8a8",
        "color-indicator-widget-background": "#303335",
        # Fix for xarray injected theme error in auto*dark mode
        # Note: because these are set with the selector
        #   body:not([data-theme="light"]), any variable that uses them needs to
        #   have a scope smaller than body. 
        #   However, the xarray variables that use these are defined in the :root selector,
        #   which is higher than body. We therefore need to redefine them in body.
        #   This is done in xarray.css, included at the bottom of this file.
        # furo issue to track when this is no longer needed:
        #   https://github.com/pradyunsg/furo/discussions/790
        "jp-content-font-color0": "rgba(255, 255, 255, 1)",
        "jp-content-font-color2": "rgba(255, 255, 255, 0.54)",
        "jp-content-font-color3": "rgba(255, 255, 255, 0.38)",
        "jp-border-color0": "#1F1F1F",
        "jp-border-color1": "#1F1F1F",
        "jp-border-color2": "#1F1F1F",
        "jp-layout-color0": "#111111",
        "jp-layout-color1": "#111111",
        "jp-layout-color2": "#313131",
        "jp-layout-color3": "#515151",
    },
    "light_css_variables": {
        "color-table-rows-even": "#eeebee",
        "color-copybutton": "#000",
        "color-indicator-text": "#5a5c63",
        "color-indicator-background": "#eeebee",
        "color-indicator-widget-text": "#2f2f2f",
        "color-indicator-widget-background": "#bdbdbd",
        # (consistency for light and dark themes, so variables are unset when switching to light)
        "jp-content-font-color0": "rgba(0, 0, 0, 1)",
        "jp-content-font-color2": "rgba(0, 0, 0, 0.54)",
        "jp-content-font-color3": "rgba(0, 0, 0, 0.38)",
        "jp-border-color0": "#e0e0e0",
        "jp-border-color1": "#e0e0e0",
        "jp-border-color2": "#e0e0e0",
        "jp-layout-color0": "#ffffff",
        "jp-layout-color1": "#ffffff",
        "jp-layout-color2": "#eeeeee",
        "jp-layout-color3": "#bdbdbd",
    },
}

html_sidebars = {
    "**": [
        "sidebar/scroll-start.html",
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
    ]
}

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = "logos/xclim-logo.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_dynamic", "logos", "_static"]

# -- Options for HTMLHelp output ---------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "xclimdoc"

# -- Options for LaTeX output ------------------------------------------

latex_engine = "pdflatex"
latex_logo = "logos/xclim-logo-light.png"

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    "papersize": "letterpaper",
    # The font size ('10pt', '11pt' or '12pt').
    "pointsize": "10pt",
    # Additional stuff for the LaTeX preamble.
    "preamble": r"""
\renewcommand{\v}[1]{\mathbf{#1}}
\nocite{*}
""",
    # Latex figure (float) alignment
    "figure_align": "htbp",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto, manual, or own class]).
latex_documents = [
    (
        root_doc,
        "xclim.tex",
        "xclim Documentation",
        "xclim Project Development Team",
        "manual",
    )
]

# -- Options for manual page output ------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        root_doc,
        "xclim",
        "xclim Documentation",
        [author],
        1,
    )
]

# -- Options for Texinfo output ----------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        root_doc,
        "xclim",
        "xclim Documentation",
        author,
        "xclim",
        "One line description of project.",
        "Miscellaneous",
    )
]


def setup(app):
    app.add_css_file("style.css")
    app.add_css_file("xarray.css")
