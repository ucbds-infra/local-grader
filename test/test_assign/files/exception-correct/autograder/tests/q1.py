from otter.test_files import test_case

OK_FORMAT = False

name = "q1"
points = None

@test_case(points=2, hidden=False, 
    success_message="Congrats you passed this test case!", 
    failure_message="This is not an int.")
def test_type(x):
    assert isinstance(x, int)
    assert 0 < x < 100

@test_case(points=2, hidden=True)
def test_value(x):
    assert x == 2

