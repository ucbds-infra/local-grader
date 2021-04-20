"""
OK-formatted test parsers and builders for Otter Assign
"""

import re
import pprint
import yaml
import nbformat

from collections import namedtuple

from .constants import TEST_REGEX, TEST_META_REGEX, OTTR_TEST_NAME_REGEX, OTTR_TEST_FILE_TEMPLATE
from .utils import get_source, lock, str_to_doctest

Test = namedtuple('Test', ['input', 'output', 'hidden', 'points', 'success_message', 'failure_message'])
OttrTest = namedtuple('OttrTest', ['name', 'hidden', 'body'])


def is_test_cell(cell):
    """
    Returns whether the current cell is a test cell
    
    Args:
        cell (``nbformat.NotebookNode``): a notebook cell

    Returns:
        ``bool``: whether the cell is a test cell
    """
    if cell.cell_type != 'code':
        return False
    source = get_source(cell)
    return source and (re.match(TEST_REGEX, source[0], flags=re.IGNORECASE) or re.match(TEST_META_REGEX, "".join(source), flags=re.IGNORECASE))

def any_public_tests(test_cases):
    """
    Returns whether any of the ``Test`` named tuples in ``test_cases`` are public tests.

    Args:
        test_cases (``list`` of ``Test`` or ``OttrTest``): list of test cases
    
    Returns:
        ``bool``: whether any of the tests are public
    """
    return any(not test.hidden for test in test_cases)

def read_test(cell, question, assignment):
    """
    Returns the contents of a test as an ``(input, output, hidden, points, success_message, failure_message)`` named tuple
    
    Args:
        cell (``nbformat.NotebookNode``): a test cell
        question (``dict``): question metadata
        assignment (``otter.assign.assignment.Assignment``): the assignment configurations

    Returns:
        ``Test`` or ``OttrTest``: test named tuple
    """
    hidden = bool(re.search("hidden", get_source(cell)[0], flags=re.IGNORECASE))
    output = ''
    for o in cell['outputs']:
        output += ''.join(o.get('text', ''))
        results = o.get('data', {}).get('text/plain')
        if results and isinstance(results, list):
            output += results[0]
        elif results:
            output += results

    # do we want to allow # BEGIN HIDDEN TEST
    BEGIN = "# BEGIN TEST"
    END = "# END TEST"
    lines = get_source(cell)

    has_metadata = False
    points = None
    success_message = None
    failure_message = None

    # parse through the test cell block
    # default values to be None, will set in ok_test.py and __init__.py if needed
    # alternatively, can set now or try in notebook_transformer.py
    for i, line in enumerate(lines):
        if line.rstrip().endswith(END):
            break
        elif line.rstrip().endswith(BEGIN):
            has_metadata = True
        elif not has_metadata:
            break
        elif line.rstrip().startswith("points"):
            value = line.rstrip().split(":")
            points = value[-1].strip()
        elif line.rstrip().startswith("hidden"):
            value = line.rstrip().split(":")
            hidden = "true" in value[-1].strip().lower() or "true" == value[-1].strip().lower()
        elif line.rstrip().startswith("success_message"):
            value = line.rstrip().split(":")
            success_message = value[-1].strip()
        elif line.rstrip().startswith("failure_message"):
            value = line.rstrip().split(":")
            failure_message = value[-1].strip()
        elif len(line.rstrip()) <= 1:
            continue
        elif ":" not in line.rstrip():
            raise ValueError(
                "Error in test metadata"
            )

    return Test('\n'.join(get_source(cell)[1:]), output, hidden, points, success_message, failure_message)

def gen_test_cell(question, tests, tests_dict, assignment):
    """
    Parses a list of test named tuples and creates a single test file. Adds this test file as a value
    to ``tests_dict`` with a key corresponding to the test's name, taken from ``question``. Returns
    a code cell that runs the check on this test.
    
    Args:
        question (``dict``): question metadata
        tests (``list`` of ``Test``): tests to be written
        tests_dict (``dict``): the tests for this assignment
        assignment (``otter.assign.assignment.Assignment``): the assignment configurations

    Returns:
        ``nbformat.NotebookNode``: code cell calling ``otter.Notebook.check`` on this test
    """
    cell = nbformat.v4.new_code_cell()

    cell.source = ['grader.check("{}")'.format(question['name'])]

    suites = [gen_suite(tests)]
    points = question.get('points', 1)
    if isinstance(points, dict):
        points = points.get('each', 1) * len(suites[0]['cases'])
    elif isinstance(points, list):
        if len(points) != len(tests):
            raise ValueError(
                f"Error in question {question['name']}: length of 'points' is {len(points)} but there "
                f"are {len(tests)} tests"
            )
    
    test = {
        'name': question['name'],
        'points': points,
        'suites': suites,
    }

    tests_dict[question['name']] = test
    lock(cell)
    return cell

def gen_suite(tests):
    """
    Generates an OK test suite for a list of tests as named tuples
    
    Args:
        tests (``list`` of ``otter.assign.Test``): test cases

    Returns:
        ``dict``: OK test suite
    """
    cases = [gen_case(test) for test in tests]
    return  {
      'cases': cases,
      'scored': True,
      'setup': '',
      'teardown': '',
      'type': 'doctest'
    }

def gen_case(test):
    """
    Generates an OK test case for a test named tuple
    
    Args:
        test (``otter.assign.Test``): OK test for this test case

    Returns:
        ``dict``: the OK test case
    """
    code_lines = str_to_doctest(test.input.split('\n'), [])

    END = "# END TEST"
    # Need to define a new index as we might night just have one line to define test metadata
    new_start_index = -1
    for i in range(len(code_lines) - 1):
        if code_lines[i].rstrip().endswith(END):
            new_start_index = i
        if code_lines[i+1].startswith('>>>') and len(code_lines[i].strip()) > 3 and not code_lines[i].strip().endswith("\\"):
            code_lines[i] += ';'

    code_lines = code_lines[new_start_index+1:]
    code_lines.append(test.output)
    points = None
    if test.points != None:
        points = float(test.points)
    return {
        'code': '\n'.join(code_lines),
        'hidden': test.hidden,
        'points': points, 
        'success_message': test.success_message, 
        'failure_message': test.failure_message, 
        'locked': False
    }

def write_test(path, test):
    """
    Writes an OK test file
    
    Args:
        path (``str``): path of file to be written
        test (``dict``): OK test to be written
    """
    with open(path, 'w') as f:
        if isinstance(test, dict):
            f.write('test = ')
            pprint.pprint(test, f, indent=4, width=200, depth=None)
        else:
            f.write(test)

def remove_hidden_tests_from_dir(test_dir, assignment):
    """
    Rewrites test files in a directory to remove hidden tests
    
    Args:
        test_dir (``pathlib.Path``): path to test files directory
        assignment (``otter.assign.assignment.Assignment``): the assignment configurations
    """
    for f in test_dir.iterdir():
        if f.name == '__init__.py' or f.suffix != '.py':
            continue
        locals = {}
        with open(f) as f2:
            exec(f2.read(), globals(), locals)
        test = locals['test']
        for suite in test['suites']:
            for i, case in list(enumerate(suite['cases']))[::-1]:
                if case['hidden']:
                    suite['cases'].pop(i)
                    if isinstance(test['points'], list):
                        test['points'].pop(i)
        write_test(f, test)
