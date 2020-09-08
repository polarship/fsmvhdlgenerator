"""Tests for the filtered_collections module."""

import pytest

from fsmvhdlgenerator.utils.filtered_collections import (FilteredDict,
                                                         FilteredSet)


class StringSet(FilteredSet):
    """An implementation of the FilteredSet container, containing strings."""
    def _value_filter(self, value):
        return str(value)


@pytest.fixture(name='test_strings')
def _test_strings():
    return StringSet(("1", 2))


class TestFilteredSet:
    """Test the StringSet implementation of FilteredSet."""
    def test_init(self, test_strings):
        """Test creation of a StringSet, where all members are strings."""
        for string in test_strings:
            assert isinstance(string, str)

    def test_contains(self, test_strings):
        """Test containment."""
        assert "2" in test_strings

    def test_iter(self, test_strings):
        """Test iteration."""
        for string in test_strings:
            assert string in ("1", "2")

    def test_len(self, test_strings):
        """Test size."""
        assert len(test_strings) == 2

    def test_add(self, test_strings):
        """Test addition of new members converted to strings as needed."""
        test_strings.add(3)
        assert "3" in test_strings

    def test_discard(self, test_strings):
        """Test removal of new members converted to strings as needed."""
        test_strings.discard(3)
        assert "3" not in test_strings

    def test_operators(self):
        """Test intersection of StringSet elements."""
        assert StringSet(range(2)) & StringSet(range(3)) == StringSet(range(2))


class StringRanks(FilteredDict):
    """An example implementation of a FilteredDict container."""
    def name_filter(self, name):
        """Return the name as a string."""
        return str(name)

    def value_filter(self, value):
        """Return the value as an int."""
        return int(value)


@pytest.fixture(name='test_items')
def _test_items():
    string_ranks = StringRanks()
    string_ranks["1"] = 0
    string_ranks["hi"] = "1"
    string_ranks[2] = 3
    return string_ranks


class TestFilteredDict:
    """Test an StringRaks implementation of FilteredDict."""
    def test_init(self, test_items):
        """Test creation of a StringRank dictionary.

        In StringRank, all keys are strings and all values are ints.

        """
        for key, value in test_items.items():
            assert isinstance(key, str)
            assert isinstance(value, int)

    def test_getitem(self, test_items):
        """Test retrieval of values by key."""
        assert test_items['1'] == 0
        assert test_items['hi'] == 1
        assert test_items['2'] == 3

    def test_setitem(self, test_items):
        """Test coercion of keys and values to correct types."""
        test_items[5] = "6"
        assert test_items['5'] == 6

    def test_delitem(self, test_items):
        """Test deletion of key-value pairs."""
        del test_items['1']
        assert '1' not in test_items
