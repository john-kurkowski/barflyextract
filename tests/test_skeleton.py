# -*- coding: utf-8 -*-

import pytest
from barflyextract.skeleton import fib

__author__ = "John Kurkowski"
__copyright__ = "John Kurkowski"
__license__ = "proprietary"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
