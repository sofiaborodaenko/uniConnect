"""
Generate a list of recommendations of events based on colleges, faculties, preferred categories.
"""
from typing import List, Dict
from event import generate_tree, EventTree, Event

FACULTY_KEYWORDS = {
    'arts': ['theatre', 'history', 'philosophy', 'literature', 'drama', 'painting', 'creative writing',
             'art', 'artist'],
    'science': ['biology', 'chemistry', 'physics', 'neuroscience', 'data science', 'lab', 'science'],
    'medicine': ['clinical', 'health', 'diagnosis', 'patient', 'hospital', 'medical', 'medicine'],
    'law': ['justice', 'legal', 'trial', 'court', 'constitution', 'law'],
    'management': ['business', 'finance', 'startup', 'entrepreneur', 'marketing', 'management'],
    'music': ['concert', 'music', 'instrument', 'composition', 'jazz', 'classical', 'music'],
    'education': ['teaching', 'curriculum', 'pedagogy', 'learning', 'classroom', 'education'],
    'dentistry': ['oral', 'dental', 'teeth', 'clinic', 'dentist', 'dentistry'],
    'public health': ['epidemiology', 'public health', 'vaccination', 'policy', 'disease', 'public health']
}


def get_all_events(tree: EventTree) -> List[Dict]:
    """
    Traverse the EventTree and return all events as a list of dictionaries.
    """
    return [e.to_dict() for e in tree.events_to_list() if e is not None]


def compute_score(event: Event, profile: Dict) -> float:
    """
    Compute a relevance score for a given event based on the user profile, including faculty-related keywords.
    """
    score = 0.0

    # Match by college
    if event.sorting_info[2] == profile.get('college'):
        score += 1.0

    if event.sorting_info[1] in profile.get('preferred_categories', []):
        score += 0.5

    faculty = profile.get('faculty', '').lower()
    desc = event.desc.lower()

    if faculty in FACULTY_KEYWORDS:
        keywords = FACULTY_KEYWORDS[faculty]
        if any(keyword in desc for keyword in keywords):
            score += 0.3

    return score


def recommend_events(profile: Dict, tree: EventTree, top_n: int = 5) -> List[Event]:
    """
    Recommend the top N events to a user based on their profile.
    """
    all_events = tree.events_to_list()
    scored_events = [(event, compute_score(event, profile)) for event in all_events]
    scored_events.sort(key=lambda x: x[1], reverse=True)
    recommended = [event for event, score in scored_events
                   if event.name not in profile.get('clicked_events', [])]

    return recommended[:top_n]


if __name__ == "__main__":

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['json', 'datetime', 'dataclasses'],  # Allow necessary modules
        'allowed-io': ['open', 'print'],  # The functions that perform I/O
        'max-line-length': 120,  # Allow longer lines for readability
        # 'disable': ['E1136'],  # Disable specific warnings if needed
    })

    events_tree = generate_tree()

    user_profile = {
        "college": "Innis College",
        "preferred_categories": [""],
        "faculty": "Arts",
    }

    recommendations = recommend_events(user_profile, events_tree)
    for e in recommendations:
        print(e.name, "-", e.sorting_info[2])
