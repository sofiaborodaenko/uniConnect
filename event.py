from __future__ import annotations
from typing import Any, Optional

class Event:
    #Plan: Add all attributes
    pass

class EventTree:
    # Plan: Add attributes, just subtress [], and a method to insert an event based on what the event is
    """

    Representation Invariants: 
        - 
    """
    # Private Instance Attributes: 
    #   - _root: 
    #       The item that is stores as the root of the EventTree (the university), or None if the tree is empty
    #   - _subtrees:
    #       The list of subtrees of this EventTree This attribute is empty when self._root is None.
    #       (an empty EventTree), but can also be empty when the root isn't (an EventTree of one item)
    
    _root = Optional[Any]
    _subtrees = list[EventTree]

    def __init__(self, root: Optional[Any], subtrees: list[EventTree]) -> None:
        """ Initialize an EventTree with given root and subtrees
        """

        self._root = root
        self._subtrees = subtrees

    # pass