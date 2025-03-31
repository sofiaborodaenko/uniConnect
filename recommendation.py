from event import generate_tree, EventTree
from typing import List, Dict

FACULTY_KEYWORDS = {
    'arts': ['theatre', 'history', 'philosophy', 'literature', 'drama', 'painting', 'creative writing'],
    'science': ['biology', 'chemistry', 'physics', 'neuroscience', 'data science', 'lab'],
    'medicine': ['clinical', 'health', 'diagnosis', 'patient', 'hospital', 'medical'],
    'law': ['justice', 'legal', 'trial', 'court', 'constitution'],
    'management': ['business', 'finance', 'startup', 'entrepreneur', 'marketing'],
    'music': ['concert', 'music', 'instrument', 'composition', 'jazz', 'classical'],
    'education': ['teaching', 'curriculum', 'pedagogy', 'learning', 'classroom'],
    'dentistry': ['oral', 'dental', 'teeth', 'clinic', 'dentist'],
    'public health': ['epidemiology', 'public health', 'vaccination', 'policy', 'disease']
}

def get_all_events(tree: EventTree) -> List[Dict]:
    """
    Traverse the EventTree and return all events as a list of dictionaries.
    """
    return [e.to_dict() for e in tree.events_to_list() if e is not None]

def compute_score(event: Dict, user_profile: Dict) -> float:
    """
    Compute a relevance score for a given event based on the user profile, including faculty-related keywords.
    """
    score = 0

    # Match by college
    if event.get('sorting_info')[1] == user_profile.get('college'):
        score += 1.0

    if event.get('sorting_info')[2] in user_profile.get('preferred_categories', []):
        score += 0.5

    faculty = user_profile.get('faculty', '').lower()
    desc = event.get('desc', '').lower()

    if faculty in FACULTY_KEYWORDS:
        keywords = FACULTY_KEYWORDS[faculty]
        if any(keyword in desc for keyword in keywords):
            score += 0.3

    return score

def recommend_events(user_profile: Dict, events_tree: EventTree, top_n: int = 5) -> List[Dict]:
    """
    Recommend the top N events to a user based on their profile.
    """
    all_events = get_all_events(events_tree)
    scored_events = [(event, compute_score(event, user_profile)) for event in all_events]
    scored_events.sort(key=lambda x: x[1], reverse=True)
    recommended = [event for event, score in scored_events 
                   if event['name'] not in user_profile.get('clicked_events', [])]
    return recommended[:top_n]

if __name__ == "__main__":
    events_tree = generate_tree()

    user_profile = {
        "college": "Innis",
        "preferred_categories": ["General", "Social", "Free Food"],
        "faculty": "Arts",
    }

    recommendations = recommend_events(user_profile, events_tree)
    for event in recommendations:
        print(event['name'], "-", event['sorting_info'][2])
