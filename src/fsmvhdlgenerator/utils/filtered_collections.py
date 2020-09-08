"""Contains variants of built-ins with filtered data.

This module houses classes mimicking the standard containers extended
with filters applied to their values.

"""

import collections
from abc import abstractmethod
from typing import Iterable


class FilteredDict(collections.MutableMapping):
    """An abstract dictionary, with filtered keys and values.

    FilteredDict is an abstract variant of dict with two
    abstract methods, name_filter and value_filter, controlling the keys
    and values allowed. It extends collections.MutableMapping.

    Subclasses should implement name_value and filter_value.

    """
    def __init__(self, **kwargs):
        """Create a filtereddict with the keyword arguments."""
        self.__items = {
            self.name_filter(k): self.value_filter(v)
            for k, v in kwargs.items()
        }

    def __getitem__(self, key):
        """Return a filtered item in the filtereddict."""
        return self.__items[self.name_filter(key)]

    def __setitem__(self, key, value):
        """Set a filtered item with a filtered name in the filtereddict."""
        self.__items[self.name_filter(key)] = self.value_filter(value)

    def __delitem__(self, key):
        """Delete a filtered item in the filtereddict."""
        del self.__items[self.name_filter(key)]

    def __iter__(self):
        """Return an iterator for the filtereddict."""
        return iter(self.__items)

    def __len__(self):
        """Return the size of the filtereddict."""
        return len(self.__items)

    def __contains__(self, key):
        """Return whether the filtereddict contains key."""
        return self.name_filter(key) in self.__items

    @abstractmethod
    def name_filter(self, name):
        """(Abstract) Transform and returning a key name."""
        return name

    @abstractmethod
    def value_filter(self, value):
        """(Abstract) Transform and returning a value."""
        return value


class FilteredSet(collections.MutableSet):
    """An abstract variant of the built-in set, with filtered values.

    MonotonicSet is a variant on the regular set with an abstract
    method, _value_filter, controlling the values allowed.

    It extends collections.MutableSet.

    """
    def __init__(self, elements: Iterable = tuple()):
        """Create a filteredset from the elements."""
        self.__elements = set((self._value_filter(e) for e in elements))

    def __contains__(self, element):
        """Return whether element is contained by the filteredset."""
        return element in self.__elements

    def __iter__(self):
        """Return an iterator for the filteredset's elements."""
        return iter(self.__elements)

    def __len__(self):
        """Return the number of elements in the filteredset."""
        return len(self.__elements)

    def add(self, value):
        """Add a filtered element to the filteredset."""
        return self.__elements.add(self._value_filter(value))

    def discard(self, value):
        """Add an (unfiltered) element from the filteredset."""
        return self.__elements.discard(value)

    @abstractmethod
    def _value_filter(self, value):
        """(Abstract) Transform and return a value."""
        return value


def MonotonicSet(element_type):
    """Return a set that can only contain element_types.

    The set class returned is suitable for sub-classing.

    Args:
        element_type: The type of elements allowed in the set.

    """
    class Cls(FilteredSet):
        """The mono-typed set to be created."""
        def _value_filter(self, value):
            """Provide the filter for FilteredList abstract base class."""
            if not isinstance(value, element_type):
                raise TypeError("Element is not of type: " + str(element_type))
            return value

    return Cls
