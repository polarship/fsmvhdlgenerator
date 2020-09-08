"""Contains the UniversalDict, a shared monostate dictionary."""

from typing import Any, Dict


class UniversalDict:
    """A dict-like container based on the monostate pattern.

    This class, when instantiated, stores keyword arguments into an internal
    dictionary stored as a class variable. Retrieval of these values can
    be retrieved like dicts, and are retrieved from the class variable.

    The net effect is that the state of this class is shared among all
    instances. Additionally, the only way to modify the state is by
    instantiating a new instance, discouraging complex traces associated with
    objects with universal state like this one.

    """

    _shared_state: Dict[str, Any] = {}

    def __init__(self, **kwargs: Any):
        """Create a new instance of the UniversalDict.

        Args:
            **kwargs: Keyword arguments saved into the dictionary stored as a
                class variable.

        """
        self.__dict__ = self._shared_state
        for key, val in kwargs.items():
            self._shared_state[key] = val

    def __getitem__(self, key: str) -> Any:
        """Return the value stored with the given key."""
        return self._shared_state[key]

    def __setitem__(self, key: str, value: Any):
        """Intentionally blank to reduce complexity."""
