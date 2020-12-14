"""
Utilities for Otter Run
"""

import re
import nbformat

from ...utils import get_source

def replace_notebook_instances(nb_path):
    """
    Replaces the creation of ``otter.Notebook`` instances in a notebook at ``nb_path`` that have custom 
    test paths with the default for Gradescope.

    Args:
        nb_path (``str``): path to the notebook
    """
    nb = nbformat.read(nb_path, as_version=nbformat.NO_CONVERT)

    instance_regex = r"otter.Notebook\([\"'].+[\"']\)"
    for cell in nb['cells']:
        source = get_source(cell)
        for i, line in enumerate(source):
            line = re.sub(instance_regex, "otter.Notebook()", line)
            source[i] = line
        cell['source'] = "\n".join(source)

    nbformat.write(nb, nb_path)
