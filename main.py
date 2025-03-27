from flask import Flask, request, jsonify, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = "password"


class UserInfoForm(FlaskForm):
    college = StringField("What College Are You In?")  # if want validators then, valdiators=[DataRequired()]
    major = StringField("What Major Are You In?")
    preferred_categories = StringField("What Are Your Preferred Categories?")
    submit = SubmitField("Submit")


def load_event_data():
    """
        Opens the two even json files
    """
    with open("static/scraped_events.json", "r") as file:
        tree_version = json.load(file)

    with open("static/u_of_t_events.json", "r") as file:
        list_version = json.load(file)

    print("tree_version: ", tree_version)
    return tree_version, list_version


def get_event_data(node):
    """
    """
    if not node:
        return []

    result = []

    for subtree in node.get("subtrees", []):
        root = subtree.get("root", {})
        children = get_event_data(subtree)
        result.append({"name": root.get("name", "Unknown"), "children": children})

    return result


@app.route("/", methods=['POST', 'GET'])  # default route
def index():
    """
    Renders the main page html
    """
    print("index running")

    tree_event_data = load_event_data()[0]
    tree_event_structure = get_event_data(tree_event_data)
    tree_event_structure_list = load_event_data()[1]

    print(tree_event_structure)
    print("list: ", tree_event_structure_list)

    college = None  # initializes the values of the user form to none
    major = None
    preferred_categories = None
    form = UserInfoForm()

    # if the checkboxes were previously clicked, sends info to the frontend
    try:
        with open("static/user_selected_filters.json", "r") as file:
            selected_filters = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        selected_filters = {"categories": [], "days": [], "colleges": []}

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
                           events_tree=tree_event_structure,
                           events_list=tree_event_structure_list)


@app.route("/update-selection", methods=["POST"])
def update_selection():
    """
    As of now, prints the checkboxes that are clicked by the user
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

    print("selected categories:", categories)
    print("selected days:", days)
    print("selected colleges:", colleges)

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
