OK_FORMAT = True

test = {   'name': 'q1',
    'points': 2,
    'suites': [   {   'cases': [   {'code': '>>> isinstance(x, int)\nTrue', 'hidden': False, 'locked': False},
                                   {'code': '>>> None\n', 'hidden': False, 'locked': False},
                                   {'code': '>>> 0 < x < 100\nTrue', 'hidden': False, 'locked': False},
                                   {'code': '>>> x\n2', 'hidden': True, 'locked': False},
                                   {'code': ">>> str(print(x))\n2\n'None'", 'hidden': True, 'locked': False}],
                      'scored': True,
                      'setup': '',
                      'teardown': '',
                      'type': 'doctest'}]}
