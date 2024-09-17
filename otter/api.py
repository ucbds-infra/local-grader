"""A programmatic API for using Otter-Grader"""

__all__ = ["export_notebook", "grade_submission"]

import os

from contextlib import nullcontext, redirect_stdout

from .export import export_notebook
from .run import main as run_grader


def grade_submission(submission_path, ag_path="autograder.zip", quiet=False, debug=False):
    """
    Runs non-containerized grading on a single submission at ``submission_path`` using the autograder
    configuration file at ``ag_path``.

    Creates a temporary grading directory using the ``tempfile`` library and grades the submission
    by replicating the autograder tree structure in that folder and running the autograder there. Does
    not run environment setup files (e.g. ``setup.sh``) or install requirements, so any requirements
    should be available in the environment being used for grading.

    Print statements executed during grading can be suppressed with ``quiet``.

    Args:
        submission_path (``str``): path to submission file
        ag_path (``str``): path to autograder zip file
        quiet (``bool``, optional): whether to suppress print statements during grading; default
            ``False``
        debug (``bool``, optional): whether to run the submission in debug mode (without ignoring
            errors)

    Returns:
        ``otter.test_files.GradingResults``: the results object produced during the grading of the
            submission.
    """
    if quiet:
        f = open(os.devnull, "w")
        cm = redirect_stdout(f)
    else:
        cm = nullcontext()

    with cm:
        results = run_grader(
            submission_path, autograder=ag_path, output_dir=None, no_logo=True, debug=debug
        )

    if quiet:
        f.close()

    return results
