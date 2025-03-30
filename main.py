import copy
from datetime import datetime

from charset_normalizer.md import annotations
from flask import Flask, request, jsonify, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import json
import event


def create_app():
    """Factory function to create and configure the Flask app"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "password"

    with app.app_context():
        app.config['EVENT_TREE'] = event.generate_tree()
        app.config['EVENT_LIST'] = app.config['EVENT_TREE'].events_to_list()
        app.config['EVENT_LIST_READABLE'] = app.config['EVENT_LIST']
        app.config['USER_SELECTED_FILTER'] = {'categories': [], 'days': [], 'colleges': []}
        app.config['USER_DATA'] = {}

    return app


app = create_app()


@app.route("/", methods=['POST', 'GET'])  # default route
def index():
    """
    Renders the main page html
    """
    print("index running")

    # if the checkboxes were previously clicked, sends info to the frontend
    selected_filters = app.config['USER_SELECTED_FILTER']
    event_list = app.config['EVENT_LIST']
    #print(event_list)
    app.config['EVENT_LIST_READABLE'] = change_time_readability(event_list)

    event_list = app.config['EVENT_LIST_READABLE']

    form_information = user_form_information()

    return render_template('index.html',
                           college=form_information["college"],
                           major=form_information["major"],
                           preferred_categories=form_information["preferred categories"],
                           form=form_information["form"],
                           selected_filters=selected_filters,
                           events_list=event_list)


def user_form_information() -> dict:
    """
        Collects the data if the user does the form
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

    app.config["USER_DATA"] = user_data

    print(user_data)

    user_data["form"] = form

    return user_data


@app.route('/<string:title>')
def ind_event(title):
    """
        Creates an individual page if the event was clicked on
    """
    if title == "favicon.ico":
        return "", 204  # return empty response with HTTP 204 (No Content)

    individual_event = None

    selected_filters = app.config['USER_SELECTED_FILTER']

    # iterates through the list
    for page in app.config["EVENT_LIST_READABLE"]:
        if page.name == title:  # once event is found sets it to the variable
            individual_event = page.to_dict()
            print("PAGE", individual_event)
            break

    # returns and renders a new page
    return render_template('event.html', individual_event=individual_event, selected_filters=selected_filters)


@app.route("/reset-filters", methods=["POST"])
def reset_filters():
    """
        Resets the lists if the reset filter button is clicked
    """
    app.config['USER_SELECTED_FILTER'] = {"categories": [], "days": [], "colleges": []}

    app.config['EVENT_LIST'] = app.config['EVENT_TREE'].events_to_list()

    return jsonify({"message": "Filters reset successfully"})


@app.route("/get-updated-events", methods=["GET"])
def get_updated_events():
    """
        Returns the updated events as JSON for dynamic frontend updates
    """
    return jsonify([event_copy.to_dict() for event_copy in app.config['EVENT_LIST_READABLE']])


@app.route("/update-selection", methods=["POST"])
def update_selection():
    """
        Gets the data from the checkboxes from the html and returns the necessary events
    """
    data = request.get_json()

    app.config['USER_SELECTED_FILTER']["categories"] = data.get("categories", [])
    app.config['USER_SELECTED_FILTER']["days"] = data.get("days", [])
    app.config['USER_SELECTED_FILTER']["colleges"] = data.get("colleges", [])

    #print(user_selected_filter)

    potential_filtered_events = filter_events(app.config['USER_SELECTED_FILTER'])

    if potential_filtered_events:
        app.config['EVENT_LIST'] = potential_filtered_events # stores a list of dict of filtered events
        app.config['EVENT_LIST_READABLE'] = change_time_readability(app.config['EVENT_LIST'])

    # if no checkboxes are checked set the event list to the original events
    if all(not app.config['USER_SELECTED_FILTER'][key] for key in ["categories", "days", "colleges"]):
        app.config['EVENT_LIST'] = app.config['EVENT_TREE'].events_to_list()
        app.config['EVENT_LIST_READABLE'] = change_time_readability(app.config['EVENT_LIST'])

    # changes the date of event
    #app.config['EVENT_LIST'] = change_time_readability(app.config['EVENT_LIST'])

    #print("selected categories:", user_selected_filter["categories"])
    #print("selected days:", user_selected_filter["days"])
    #print("selected colleges:", user_selected_filter["colleges"])

    return jsonify({
        "categories": app.config['USER_SELECTED_FILTER']["categories"],
        "days": app.config['USER_SELECTED_FILTER']["days"],
        "colleges": app.config['USER_SELECTED_FILTER']["colleges"]
    })


def filter_events(filter_dict: dict) -> list:
    """
        Given the dictionary containing the clicked on checkboxes, goes through the events and
        returns a list of the new events if they exist
    """
    filtered_events = []  # keeps the events after theyre filtered

    categories = filter_dict["categories"]
    days = filter_dict["days"]
    colleges = filter_dict["colleges"]

    # filter the events if the lists are populated
    if categories:
        filtered_events.extend(app.config['EVENT_TREE'].filter_tree(categories))

    if days:
        filtered_events.extend(app.config['EVENT_TREE'].filter_tree(days))

    if colleges:
        filtered_events.extend(app.config['EVENT_TREE'].filter_tree(colleges))

    #print("THE FILTERED EVENTS: ", filtered_events_for_front)
    return filtered_events


def change_time_readability(unix_events: list) -> list:
    """
        Changes the date of the event from unix stampcode to readable date
    """
    unix_event_copy = copy.deepcopy(unix_events)

    for normal_event in unix_event_copy:
        if type(normal_event.sorting_info[0]) is int:
            date = (datetime.fromtimestamp(normal_event.sorting_info[0]).strftime('%b %d, %Y'))
            normal_event.sorting_info = (date, normal_event.sorting_info[1], normal_event.sorting_info[2])

        if normal_event.post_time != 0:
            posted_time = datetime.fromtimestamp(normal_event.post_time).strftime('%Y-%m-%d %H:%M:%S')
            normal_event.post_time = posted_time

    return unix_event_copy


class UserInfoForm(FlaskForm):
    """
        UserInfoForm stores and generates a form for the user to fill out depending on their preferences
    """

    college = StringField("What College Are You In?")  # if want validators then, valdiators=[DataRequired()]
    major = StringField("What Major Are You In?")
    preferred_categories = StringField("What Are Your Preferred Categories?")
    submit = SubmitField("Submit")


if __name__ == "__main__":
    app.run(debug=True, port=8080)
