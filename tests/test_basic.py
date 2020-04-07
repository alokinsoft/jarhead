# -*- coding: utf-8 -*-

from .context import jarhead
import unittest
import pytest


def test_flatten():
    from jarhead.views.structure.utils import flatten
    f = flatten

    assert f([]) == [], "flatten of empty list is empty list"
    assert f([1]) == [1], "flatten of single element list is a single element list"
    assert f([[1]]) == [1], "flattening a nested list creates a simple list"
    assert f([1, [2]]) == [1, 2]

