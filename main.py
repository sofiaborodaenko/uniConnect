from flask import Flask, request, jsonify, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import json
import event
import scrapper

app = Flask(__name__)
app.config['SECRET_KEY'] = "password"


class UserInfoForm(FlaskForm):
    college = StringField("What College Are You In?")  # if want validators then, valdiators=[DataRequired()]
    major = StringField("What Major Are You In?")
    preferred_categories = StringField("What Are Your Preferred Categories?")
    submit = SubmitField("Submit")


@app.route('/event/<string:title>')
def ind_event(title):
    """
        Gets the name of the event that the user clicks on and renders a new page
    """
    individual_event = {}
    events = load_event_data()[0]  # loads the events and stores them in a list

    # iterates through the list
    for page in events:
        if page['name'] == title:  # once event is found sets it to the variable
            individual_event = page

    # returns and renders a new page
    return render_template('event.html', individual_event=individual_event)


def load_event_data():
    """
        Opens the event json file
    """
    with open("static/u_of_t_events.json", "r") as file:
        list_version = json.load(file)

    with open("static/u_of_t_events_original.json", "r") as file:
        list_version_original = json.load(file)

    return list_version, list_version_original


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

    tree_event_structure_list = load_event_data()[0]
    # print(tree_event_structure)
    # print("list: ", tree_event_structure_list)

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

    return render_template('index.html',
                           college=college,
                           major=major,
                           preferred_categories=preferred_categories,
                           form=form,
                           selected_filters=selected_filters,
                           events_list=tree_event_structure_list)


@app.route("/update-selection", methods=["POST"])
def update_selection():
    """
        Gets the categories the user selected, creates a json file with the lists,
        filters the u_of_t_events.json.
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

    # creates a json file containing the selected filters
    with open('static/user_selected_filters.json', 'w') as file:
        json.dump(user_selection, file, indent=4)

    # print("selected categories:", categories)
    # print("selected days:", days)
    # print("selected colleges:", colleges)

    # generates a tree from the u_of_t_events.json
    uoft_event_tree = event.generate_tree()
    filtered_events = []  # keeps the events after theyre filtered
    filtered_events_for_json = []  # keeps the evens after they're convereted to a dict

    # filter the events if the lists are populated
    if categories:
        filtered_events.extend(uoft_event_tree.filter_tree(categories))

    if days:
        filtered_events.extend(uoft_event_tree.filter_tree(days))

    if colleges:
        filtered_events.extend(uoft_event_tree.filter_tree(colleges))

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
            json.dump(original_events, file, indent=4)

    return jsonify({
        "categories": categories,
        "days": days,
        "colleges": colleges
    })


@app.route("/reset-filters", methods=["POST"])
def reset_filters():
    """
    Resets the user_selected_filter.json if the reset filters button is clicked
    """

    clear_filters = {"categories": [], "days": [], "colleges": []}

    with open("static/user_selected_filters.json", "w") as file:
        json.dump(clear_filters, file, indent=4)

    original_events = load_event_data()[1]
    with open('static/u_of_t_events.json', 'w') as file:
        json.dump(original_events, file, indent=4)

    return jsonify({"message": "Filters reset successfully"})


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
    app.run(debug=True, port=8000)

#Need a method to parse data
#Import tkinter and Flask
#(Probably optional for now) Add a scrapy to scrape off sites
