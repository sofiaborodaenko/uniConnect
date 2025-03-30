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
event_list = event_tree.events_to_list()
user_selected_filter = {}
user_data = {}


@app.route("/", methods=['POST', 'GET'])  # default route
def index():
    """
    Renders the main page html
    """
    print("index running")
    global event_list, user_selected_filter

    # if the checkboxes were previously clicked, sends info to the frontend
    selected_filters = user_selected_filter or {'categories': [], 'days': [], 'colleges': []}

    print(event_list)

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
    """
    global user_data

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

    print(user_data)

    user_data["form"] = form

    return user_data


@app.route('/<string:title>')
def ind_event(title):
    global event_list, user_selected_filter

    if title == "favicon.ico":
        return "", 204  # return empty response with HTTP 204 (No Content)

    individual_event = None

    selected_filters = user_selected_filter or {'categories': [], 'days': [], 'colleges': []}

    # iterates through the list
    for page in event_list:
        if page.name == title:  # once event is found sets it to the variable
            individual_event = page.to_dict()
            print("PAGE", individual_event)
            break

    # returns and renders a new page
    return render_template('event.html', individual_event=individual_event, selected_filters=selected_filters)


@app.route("/reset-filters", methods=["POST"])
def reset_filters():
    """
    Resets the user_selected_filter.json if the reset filters button is clicked
    """
    global user_selected_filter, event_list
    user_selected_filter = {"categories": [], "days": [], "colleges": []}

    event_list = event_tree.events_to_list()

    return jsonify({"message": "Filters reset successfully"})


@app.route("/update-selection", methods=["POST"])
def update_selection():
    """

    """
    global user_selected_filter, event_list
    data = request.get_json()

    user_selected_filter["categories"] = data.get("categories", [])
    user_selected_filter["days"] = data.get("days", [])
    user_selected_filter["colleges"] = data.get("colleges", [])

    print(user_selected_filter)

    event_list = filter_events(user_selected_filter)  # stores a list of dict of filtered events

    if not event_list:
        event_list = event_tree.events_to_list()

    print("selected categories:", user_selected_filter["categories"])
    print("selected days:", user_selected_filter["days"])
    print("selected colleges:", user_selected_filter["colleges"])

    return jsonify({
        "categories": user_selected_filter["categories"],
        "days": user_selected_filter["days"],
        "colleges": user_selected_filter["colleges"]
    })


def filter_events(filter_dict: dict) -> list:
    """
    """
    filtered_events = []  # keeps the events after theyre filtered

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

    #print("THE FILTERED EVENTS: ", filtered_events_for_front)
    return filtered_events


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
