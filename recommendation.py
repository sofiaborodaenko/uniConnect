from event import generate_tree, EventTree
from typing import List, Dict

def get_all_events(tree: EventTree) -> List[Dict]:
    '''
    Traverse the EventTree and return all events as a list of dictionaries.
    '''
    return [e.to_dict() for e in tree.events_to_list() if e is not None]

def compute_score(event, user_profile):
    '''
    Compute a relevance score for a given event based on the user profile.
    '''
    score = 0
    if event.get('sorting_info')[1] == user_profile['college']:
        score += 1.0
    if event.get('sorting_info')[2] in user_profile['preferred_categories']:
        score += 0.5
    return score

def recommend_events(user_profile, events_tree: EventTree, top_n=5):
    '''
    Recommend the top N events to a user based on their profile.
    '''
    all_events = get_all_events(events_tree)
    scored_events = [(event, compute_score(event, user_profile)) for event in all_events]
    scored_events.sort(key=lambda x: x[1], reverse=True)
    recommended = [event for event, score in scored_events 
                   if event['name'] not in user_profile['clicked_events']]
    return recommended[:top_n]


if __name__ == "__main__":
    events_tree = generate_tree()

    user_profile = {
        "college": "Innis",
        "preferred_categories": ["General", "Social", "Free Food"],
    }

    recommendations = recommend_events(user_profile, events_tree)
    for event in recommendations:
        print(event['name'], "-", event['sorting_info'][2])
