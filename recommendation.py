# todo:
# 1. a function to get the user info: college, major, preferred_categories, clicked_events
# 2. a function to record the events user clicked.

# # Example user profile
# user_profile = {
#     'college': 'Trinity College',
#     'major': 'Computer Science',
#     'preferred_categories': ['Social', 'Academic'],
#     'clicked_events': ['event_123', 'event_456']
# }

# # Example tree(?
# {
#   "day": "Monday",
#   "children": [
#     {
#       "college": "Trinity College",
#       "children": [
#         {
#           "category": "Social Events",
#           "events": [
#             {"id": "A", "name": "Event A", "desc": "Description A", "college": "Trinity College", "category": "Social Events"},
#             {"id": "B", "name": "Event B", "desc": "Description B", "college": "Trinity College", "category": "Social Events"}
#           ]
#         },
#         {
#           "category": "Academic Events",
#           "events": [
#             {"id": "C", "name": "Event C", "desc": "Description C", "college": "Trinity College", "category": "Academic Events"}
#           ]
#         },
#         {
#           "category": "Free Food Events",
#           "events": [
#             {"id": "D", "name": "Event D", "desc": "Description D", "college": "Trinity College", "category": "Free Food Events"}
#           ]
#         },
#         {
#           "category": "Career Events",
#           "events": [
#             {"id": "E", "name": "Event E", "desc": "Description E", "college": "Trinity College", "category": "Career Events"}
#           ]
#         }
#       ]
#     },
#     {
#       "college": "Victoria College",
#       "children": [
#         {
#           "category": "Social Events",
#           "events": [
#             {"id": "F", "name": "Event F", "desc": "Description F", "college": "Victoria College", "category": "Social Events"}
#           ]
#         },
#         {
#           "category": "Academic Events",
#           "events": [
#             {"id": "G", "name": "Event G", "desc": "Description G", "college": "Victoria College", "category": "Academic Events"},
#             {"id": "H", "name": "Event H", "desc": "Description H", "college": "Victoria College", "category": "Academic Events"}
#           ]
#         }
#       ]
#     }, 
#     // ... 
#   ]
# }


import json

with open('events_tree.json', 'r') as f:
    events_tree = json.load(f)

def get_all_events(tree):
    events = []
    if 'events' in tree:
        events.extend(tree['events'])
    if 'children' in tree:
        for child in tree['children']:
            events.extend(get_all_events(child))
    return events

def compute_score(event, user_profile):
    # idk is this enough? or we need a more complicated algo to calculate the score?
    score = 0
    if event.get('college') == user_profile['college']:
        score += 1.0
    if event.get('category') in user_profile['preferred_categories']:
        score += 0.5
    if 'major' in user_profile and event.get('related_major') == user_profile['major']:
        score += 0.5
    return score

def recommend_events(user_profile, events_tree, top_n=5):
    all_events = get_all_events(events_tree)
    scored_events = [(event, compute_score(event, user_profile)) for event in all_events]
    scored_events.sort(key=lambda x: x[1], reverse=True)
    recommended = [event for event, score in scored_events 
                   if event['id'] not in user_profile['clicked_events']]
    return recommended[:top_n]


recommendations = recommend_events(user_profile, events_tree)
for event in recommendations:
    print(event['name'], event['category'])
