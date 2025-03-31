from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import json


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
    location: Optional[str]  # Maybe not optional?
    sorting_info: tuple[int, str, str]
    post_time: int
    image_src: Optional[str] = None

    def __init__(self, name: str, desc: str, location: str, sorting_info: tuple[int, str, str],
                 post_time: Optional[int],
                 image: Optional[str] = None):
        self.name = name
        self.desc = desc
        self.location = location
        self.sorting_info = sorting_info
        self.post_time = post_time
        self.image = image

    def to_dict(self):
        """
            Returns the event's details in a dictionary
        """

        return {"name": self.name,
                "desc": self.desc,
                "location": self.location,
                "sorting_info": self.sorting_info,
                "post_time": self.post_time,
                "image": self.image}


class EventTree:
    """Tree to store events [PLEASE PUT IN THE DESCRIPTION FOR THE LAYERS LATER]

    Instance Attributes:
       -root:
           The item stored at this tree's root, or None if the tree is empty.
       -subtrees:
           The list of subtrees of this tree. This attribute is empty when
           self._root is None (representing an empty tree). However, this attribute
           may be empty when self._root is not None, which represents a tree consisting
           of just one item.

    Representation Invariants:
        - self.root is not None or self.subtrees == []
    """
    # Private Instance Attributes:
    #
    root: Optional[Event]
    subtrees: list[EventTree]

    def __init__(self, root: Optional[Event], subtrees: list[EventTree]) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        If root is None, the tree is empty.

        Preconditions:
            - root is not none or subtrees == []
        """
        self.root = root
        self.subtrees = subtrees

    def is_empty(self) -> bool:
        """Return whether this tree is empty.
        """
        return self.root is None

    def insert(self, event: Event) -> None:
        """Insert an event into the tree according to its day, college, and category."""

        time, college, category = event.sorting_info
        event_day = datetime.fromtimestamp(time).strftime('%A')

        # Make each level
        day_tree = self._find_or_create_subtree(event_day)

        college_tree = day_tree._find_or_create_subtree(college)

        category_tree = college_tree._find_or_create_subtree(category)

        event_node = EventTree(event, [])
        category_tree.subtrees.append(event_node)

    def _find_or_create_subtree(self, name: str) -> EventTree:
        """Find a subtree, if it does not exist, create a subtree"""
        tree = self._find_subtree(name)
        if not tree:
            temp_event = Event(name, "", "", (0, "", ""), 0, "")
            new_tree = EventTree(temp_event, [])
            self.subtrees.append(new_tree)
            return new_tree
        return tree

    def _find_subtree(self, name: str) -> Optional[EventTree]:
        """Go to the correct subtree"""
        for subtree in self.subtrees:
            if subtree.root and subtree.root.name == name:
                return subtree

        return None

    def print_tree(self, level: int = 0) -> None:
        """Just prints the true"""
        if self.root:
            print("  " * level + self.root.name)
        for subtree in self.subtrees:
            subtree.print_tree(level + 1)

    def filter_tree(self, filter_tags: list[str]) -> list[Event]:
        """Given filter tags, filter all events including those tags"""
        filtered_events = []
        cur_filter = [self]

        while cur_filter:
            cur = cur_filter.pop(0)
            if cur.root and cur.root.name in filter_tags:
                potential_events = [cur]
                while potential_events:
                    event = potential_events.pop(0)
                    if not event.subtrees:
                        filtered_events.append(event.root)
                    potential_events.extend(event.subtrees)
            else:
                cur_filter.extend(cur.subtrees)

        return filtered_events

    def events_to_list(self) -> list[Event]:
        """
            Returns a list of all the events in the tree
        """
        if not self.subtrees:
            return [self.root]
        else:
            to_list = []

            for child in self.subtrees:
                if child.events_to_list():
                    to_list.extend(child.events_to_list())

            return to_list

def radix_sort_events(events: list[Event], method: str) -> list[Event]:
    """Sort by time of the event"""
    if not events:
        return []

    timestamps = [event.post_time for event in events]
    max_time = max(timestamps)

    exp = 1
    while max_time // exp > 0:
        events = _counting_sort_events(events, exp)
        exp *= 10

    if method == "new":
        return events[::-1]
    elif method == "old":
        return events

    return events

def _counting_sort_events(events: list[Event], exp: int) -> list[Event]:
    """Counting sort to help radix sort"""
    n = len(events)
    output = [None]*n
    count = [0]*10

    for event in events:
        index = (event.sorting_info[0] // exp) % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i-1]

    for event in reversed(events):
        index = (event.sorting_info[0] // exp) % 10
        output[count[index] - 1] = event
        count[index] -= 1

    return output

def search_event(events: list[Event], query: str) -> list[Event]:
    return [event for event in events if query.lower() in event.name.lower()]


def generate_tree() -> EventTree:
    """
        Given a file, create events and put them in a tree
    """
    tree = EventTree(None, [])
    with open('static/u_of_t_events_original.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    for index, event in enumerate(data, start=1):
        name = event.get('name', '').strip('"')
        desc = event.get('desc', '').strip('"')
        location = event.get('location')
        sorting_info = event.get('sorting_info')
        posted_time = event.get('posted_time')

        image = event.get('image')
        if image:
            image = image.strip('"')
        if location:
            location = location.strip('"')
        tree.insert(Event(name, desc, location, sorting_info, posted_time, image))

    return tree


def add_event_dict(given_list: list, name: str, desc: str, location: Optional[str], sorting_info: tuple[int, str, str],
                   posted_time: int, image: Optional[str]) -> None:
    """
        Appends the event in the form of a dictionary to a given list
    """

    given_list.append({
        "name": name,
        "desc": desc,
        "location": location,
        "sorting_info": sorting_info,
        "posted_time": posted_time,
        "image": image
    })


if __name__ == "__main__":
    a = EventTree(None, [])
    a.insert(Event("Eat d", "", "", (1700000000, "UC", "Free Food"), 1700000000, "image_url"))
    a.insert(Event("talk", "", "", (1700000000, "My College", "Social"), 1700000000, "image_url"))
    a.insert(Event("Eat f", "", "", (1700000000, "My College", "Free Food"), 1700000000, "image_url"))

    print(a.events_to_list())

    b = generate_tree()
    b.print_tree()

    filtered_list = b.filter_tree(["Monday"])
    newest_sorted = radix_sort_events(filtered_list, True)
    searched_list = search_event(newest_sorted, "le")

    print([x.name for x in searched_list])