import os
import sys
import pytest

# Ensure the backend project package path is available for tests run from any location
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

@pytest.mark.parametrize("text,expected", [
    ("This is good", False),
    ("This contains hate content", True),
    ("Violence and terror", True),
])
def test_blocked_keywords_work(text, expected):
    from app.openai_service import _contains_blocked
    assert _contains_blocked(text) is expected
