from flask import Flask, request, jsonify, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = "password"


class UserInfoForm(FlaskForm):
    college = StringField("What College Are You In?")  #if want validators then, valdiators=[DataRequired()]
    major = StringField("What Major Are You In?")
    preferred_categories = StringField("What Are Your Preferred Categories?")
    submit = SubmitField("Submit")


@app.route("/", methods=['POST', 'GET'])  # default route
def index():
    """
    Renders the main page html
    """

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

   # return render_template('index.html')


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

    # figure out how to clear the lists if page relods,
    # one issue may be that when user clicks to have their preferences
    # such as major, etc. page may reload automaitcally.

    # creates a json file containing the selected filters
    with open('user_selected_filters.json', 'w') as file:
        json.dump(user_selection, file, indent=4)

    print("selected categories:", categories)
    print("selected days:", days)
    print("selected colleges:", colleges)

    return jsonify({
        "categories": categories,
        "days": days,
        "colleges": colleges
    })

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
