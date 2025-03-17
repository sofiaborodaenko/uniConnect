from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


@app.route("/")  # default route
def index():
    """
    Renders the main page html
    """

    return render_template('index.html')


@app.route("/update_selection", methods=["POST"])
def update_selection():
    """
    As of now, prints the checkboxes that are clicked by the user
    """
    data = request.get_json()
    categories = data.get("categories", [])
    days = data.get("days", [])
    colleges = data.get("colleges", [])

    print("selected categories:", categories)
    print("selected days:", days)
    print("selected colleges:", colleges)

    return jsonify({
        "categories": categories,
        "days": days,
        "colleges": colleges
    })

if __name__ == "__main__":
    app.run(debug=True)

#Need a method to parse data
#Import tkinter and Flask
#(Probably optional for now) Add a scrapy to scrape off sites
