from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Event:
    """
    Event node to store all College event information

    Instance Attributes:
        - name: Name of the event as a string
        - desc: Description of the event as a string
        - location: Location of the event as a string
        - sorting_info: Tuple of time, college, and category for sorting, as int, string, string respectively
        - post_time: Posted time of the event in UNIX time
        - image_src: The image of the event if available as an image url
    """

    name: str
    desc: str
    location: Optional[str] # Maybe not optional?
    sorting_info: tuple[int, str, str]
    post_time: int
    image_src: Optional[str] = None

    def __init__(self, name: str, desc: str, location: str, sorting_info: tuple[int, str, str], post_time: int, image: Optional[str] = None):
        self.name = name
        self.desc = desc
        self.location = location
        self.sorting_info = sorting_info
        self.post_time = post_time
        self.image = image



class EventTree:
    """Tree to store events [PLEASE PUT IN THE DESCRIPTION FOR THE LAYERS LATER]

    Representation Invariants:
        - self._root is not None or self._subtrees == []
    """
    # Private Instance Attributes:
    #   - _root:
    #       The item stored at this tree's root, or None if the tree is empty.
    #   - _subtrees:
    #       The list of subtrees of this tree. This attribute is empty when
    #       self._root is None (representing an empty tree). However, this attribute
    #       may be empty when self._root is not None, which represents a tree consisting
    #       of just one item.
    _root: Optional[Event]
    _subtrees: list[EventTree]

    def __init__(self, root: Optional[Event], subtrees: list[EventTree]) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        If root is None, the tree is empty.

        Preconditions:
            - root is not none or subtrees == []
        """
        self._root = root
        self._subtrees = subtrees

    def is_empty(self) -> bool:
        """Return whether this tree is empty.
        """
        return self._root is None

    def insert(self, event: Event) -> None:
        """Insert an event into the tree according to its day, college, and category."""

        time, college, category = event.sorting_info
        event_day = datetime.fromtimestamp(time).strftime('%A')

        #Make each level
        day_tree = self._find_or_create_subtree(event_day)

        college_tree = day_tree._find_or_create_subtree(college)

        category_tree = college_tree._find_or_create_subtree(category)


        event_node = EventTree(event, [])
        category_tree._subtrees.append(event_node)

    def _find_or_create_subtree(self, name: str) -> EventTree:
        """Go to the correct subtree, if it doesn't exist, create it."""
        for subtree in self._subtrees:
            if subtree._root and subtree._root.name == name:
                return subtree

        temp_event = Event(name,"","",(0,"",""), 0,"")
        new_tree = EventTree(temp_event, [])
        self._subtrees.append(new_tree)
        return new_tree

    def print_tree(self, level:int = 0) -> None:
        """Just prints the true"""
        if self._root:
            print("  " * level + self._root.name)
        for subtree in self._subtrees:
            subtree.print_tree(level + 1)

a = EventTree(None, [])
a.insert(Event("Event A", "", "", (1700000000, "College A", "Category A"), 1700000000, "image_url"))
a.insert(Event("Event B", "", "", (1700000000, "College B", "Category B"), 1700000000, "image_url"))
a.print_tree()