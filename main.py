from datetime import datetime

from flask import Flask, request, jsonify, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import json
import event

app = Flask(__name__)
app.config['SECRET_KEY'] = "password"

event_tree = event.generate_tree()

def original_event_tree_to_list(append_list: list) -> list:
    """
    """
    for events in event_tree.events_to_list():
        event.add_event_dict(
            append_list,
            events.name,
            events.desc,
            events.location,
            events.sorting_info,
            events.post_time,
            events.image

        )

    return append_list


@app.route("/", methods=['POST', 'GET'])  # default route
def index():
    """
    Renders the main page html
    """
    print("index running")

    # if the checkboxes were previously clicked, sends info to the frontend
    try:
        with open("static/user_selected_filters.json", "r") as file:
            selected_filters = json.load(file)
            print(selected_filters)
    except (FileNotFoundError, json.JSONDecodeError):
        selected_filters = {"categories": [], "days": [], "colleges": []}


    tree_event_structure_list = load_event_data()

    # tree_event_structure_list = load_event_data()[0]  # loads the even list
    # print(tree_event_structure)
    # print("list: ", tree_event_structure_list)

    #user_checkbox_info = update_selection()  # gets dict of the lists
    """event_lists = filter_events(user_checkbox_info)  # stores a list of dict of filtered events

    if event_lists is []:
        for events in event_tree.events_to_list():
            event.add_event_dict(
                event_lists,
                events.name,
                events.desc,
                events.location,
                events.sorting_info,
                events.post_time,
                events.image

            )"""

    form_information = user_form_information()

    return render_template('index.html',
                           college=form_information["college"],
                           major=form_information["major"],
                           preferred_categories=form_information["preferred categories"],
                           form=form_information["form"],
                           selected_filters=selected_filters,
                           events_list=tree_event_structure_list)


def user_form_information() -> dict:
    """
    """
    college = None  # initializes the values of the user form to none
    major = None
    preferred_categories = None
    form = UserInfoForm()

    # validating the form
    if form.validate_on_submit():
        college = form.college.data  # assigning the data to the variables
        major = form.major.data
        preferred_categories = form.preferred_categories.data

        form.college.data = ''  # resetting the values
        form.major.data = ''
        form.preferred_categories.data = ''

    # resets the values in the user_data if the reset button is clicked
    if request.form.get('reset'):
        form.college.data = ''  # resetting the values
        form.major.data = ''
        form.preferred_categories.data = ''

    user_data = {
        "college": college,
        "major": major,
        "preferred categories": preferred_categories
    }

    # saves the info as a json file
    with open("static/user_data.json", "w") as file:
        json.dump(user_data, file, indent=4)

    user_data["form"] = form

    return user_data


@app.route('/<string:title>')
def ind_event(title):

    if title == "favicon.ico":
        return "", 204  # return empty response with HTTP 204 (No Content)

    individual_event = None
    events = load_event_data()  # loads the events and stores them in a list

    # iterates through the list
    for page in events:
        if page['name'] == title:  # once event is found sets it to the variable
            individual_event = page
            break

    # returns and renders a new page
    return render_template('event.html', individual_event=individual_event)


def load_event_data():
    """
        Opens the event json file


    #with open("static/u_of_t_events.json", "r") as file:
    #list_version = json.load(file)

    original_events = []
    original_events = original_event_tree_to_list(original_events)


    with open("static/events.json", "w") as file:
        json.dump(original_events, file, indent=4)"""

    with open("static/events.json", "r") as file:
        list_events_json = json.load(file)




    # if type(sorting_info[0]) is int:
    #    sorting_info_date = datetime.fromtimestamp(sorting_info[0]).strftime('%b %d, %Y')
    #    sorting_info = (sorting_info_date, sorting_info[1], sorting_info[2])

    # if posted_time != 0:
    #    posted_time = datetime.fromtimestamp(posted_time).strftime('%Y-%m-%d %H:%M:%S')

    # iteraties through the event list and converts the time for readability
    """for list_event in list_version:
        if type(list_event['sorting_info'][0]) is int:
            date = (datetime.fromtimestamp(list_event['sorting_info'][0]).strftime('%b %d, %Y'))
            list_event['sorting_info'] = (date, list_event['sorting_info'][1], list_event['sorting_info'][2])

        if list_event['posted_time'] != 0:
            posted_time = datetime.fromtimestamp(list_event['posted_time']).strftime('%Y-%m-%d %H:%M:%S')
            list_event['posted_time'] = posted_time"""

    return list_events_json


@app.route("/reset-filters", methods=["POST"])
def reset_filters():
    """
    Resets the user_selected_filter.json if the reset filters button is clicked
    """

    clear_filters = {"categories": [], "days": [], "colleges": []}

    with open("static/user_selected_filters.json", "w") as file:
        json.dump(clear_filters, file, indent=4)

    original_events = []
    original_events = original_event_tree_to_list(original_events)  # gets the original events that were scrapped
    with open('static/events.json', 'w') as file:
        json.dump(original_events, file, indent=4)  # repopulates the u_of_t_events.json

    return jsonify({"message": "Filters reset successfully"})


@app.route("/update-selection", methods=["POST"])
def update_selection():
    """

    """
    data = request.get_json()

    categories = data.get("categories", [])
    days = data.get("days", [])
    colleges = data.get("colleges", [])

    user_selection = {
        "categories": categories,
        "days": days,
        "colleges": colleges
    }

    print(user_selection)

    event_lists = filter_events(user_selection)  # stores a list of dict of filtered events

    if not event_lists:
        original_event_tree_to_list(event_lists)

    print("Filtered events to save:", event_lists)

    with open('static/events.json', 'w') as file:
        json.dump(event_lists, file, indent=4)

    # creates a json file containing the selected filters
    with open('static/user_selected_filters.json', 'w') as file:
        json.dump(user_selection, file, indent=4)

    print("selected categories:", categories)
    print("selected days:", days)
    print("selected colleges:", colleges)

    # generates a tree from the u_of_t_events.json
    # uoft_event_tree = event.generate_tree()
    """filtered_events = []  # keeps the events after theyre filtered
    filtered_events_for_json = []  # keeps the evens after they're convereted to a dict

    # filter the events if the lists are populated
    if categories:
        filtered_events.extend(event_tree.filter_tree(categories))

    if days:
        filtered_events.extend(event_tree.filter_tree(days))

    if colleges:
        filtered_events.extend(event_tree.filter_tree(colleges))

    print(filtered_events)

    # converts the filtered events to a dict form
    if filtered_events:
        for events in filtered_events:
            event.add_event_dict(
                filtered_events_for_json,
                events.name,
                events.desc,
                events.location,
                events.sorting_info,
                events.post_time,
                events.image

            )

        with open('static/u_of_t_events.json', 'w') as file:
            json.dump(filtered_events_for_json, file, indent=4)
    else:

        original_events = load_event_data()[1]
        with open('static/u_of_t_events.json', 'w') as file:
            json.dump(original_events, file, indent=4)"""

    return jsonify({
        "categories": categories,
        "days": days,
        "colleges": colleges
    })


def filter_events(filter_dict: dict) -> list:
    """
    """
    filtered_events = []  # keeps the events after theyre filtered
    filtered_events_for_front = []  # keeps the evens after they're convereted to a dict

    categories = filter_dict["categories"]
    days = filter_dict["days"]
    colleges = filter_dict["colleges"]

    # filter the events if the lists are populated
    if categories:
        filtered_events.extend(event_tree.filter_tree(categories))

    if days:
        filtered_events.extend(event_tree.filter_tree(days))

    if colleges:
        filtered_events.extend(event_tree.filter_tree(colleges))

    # converts the filtered events to a dict form
    if filtered_events:
        for events in filtered_events:
            event.add_event_dict(
                filtered_events_for_front,
                events.name,
                events.desc,
                events.location,
                events.sorting_info,
                events.post_time,
                events.image

            )

    print("THE FILTERED EVENTS: ", filtered_events_for_front)
    return filtered_events_for_front


class UserInfoForm(FlaskForm):
    """
        UserInfoForm stores and generates a form for the user to fill out depending on their preferences
    """

    college = StringField("What College Are You In?")  # if want validators then, valdiators=[DataRequired()]
    major = StringField("What Major Are You In?")
    preferred_categories = StringField("What Are Your Preferred Categories?")
    submit = SubmitField("Submit")


"""
@app.route("/user-info", methods=['GET', 'POST'])
def user_info():
    
    college = None
    major = None
    preferred_categories = None
    form = UserInfoForm()

    # validating the form
    if form.validate_on_submit():
        college = form.college.data  # assigning the data to the variables
        major = form.major.data
        preferred_categories = form.preferred_categories.data

        form.college.data = ''  # resetting the values
        form.major.data = ''
        form.preferred_categories.data = ''

    user_data = {
        "college": college,
        "major": major,
        "preferred categories": preferred_categories
    }

    # saves the info as a json file
    with open("user_data.json", "w") as file:
        json.dump(user_data, file, indent=4)

    return render_template('index.html',
                           college=college,
                           major=major,
                           preferred_categories=preferred_categories,
                           form=form)

"""

if __name__ == "__main__":
    app.run(debug=True, port=8080)

#Need a method to parse data
#Import tkinter and Flask
#(Probably optional for now) Add a scrapy to scrape off sites
