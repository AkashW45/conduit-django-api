import pytest
from conduit.apps.articles import compute_reading_time

# Happy path: parametrize different word counts and expected rounded minutes
@pytest.mark.parametrize("body, expected", [
    ("This is a short text.", 1),
    ("a " * 199, 1),   # 199 words -> 0.995, ceil=1, max(1)=1
    ("a " * 200, 1),   # exactly 200 words -> ceil(1)=1
    ("a " * 201, 2),   # 201 words -> ceil(1.005)=2
    ("word " * 500, 3), # 500 words -> 2.5, ceil=3
    ("a " * 1000, 5),  # 1000 words -> 5, ceil=5
])
def test_reading_time_happy_path(body, expected):
    assert compute_reading_time(body) == expected

# Edge case: empty or whitespace-only body returns 1 (minimum)
def test_reading_time_empty_or_whitespace():
    assert compute_reading_time("") == 1
    assert compute_reading_time("    ") == 1
    assert compute_reading_time("\t\n") == 1

# Edge case: punctuation doesn't affect word splitting (based on whitespace)
def test_reading_time_with_punctuation():
    assert compute_reading_time("Hello, world!") == 1      # 2 words
    # 6 words
    assert compute_reading_time("Hello, world! This is a test.") == 1
    # 200 punctuated words
    body = "a! b? c: d; e. " * 40   # 5*40 = 200 words
    assert compute_reading_time(body) == 1

# Edge case: body with newlines and multiple spaces still splits correctly
def test_reading_time_newlines_and_multiple_spaces():
    body = "one  two\nthree   four"
    assert compute_reading_time(body) == 1

# Error path: passing None or non‑string raises AttributeError
def test_reading_time_invalid_body():
    with pytest.raises(AttributeError):
        compute_reading_time(None)
    with pytest.raises(AttributeError):
        compute_reading_time(123)
    with pytest.raises(AttributeError):
        compute_reading_time([])