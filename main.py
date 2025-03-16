from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


@app.route("/")  # default route
def index():
    """
    Renders the main page html
    """
    if request.method == 'POST':
        request.form.getlist('my-checkbox')

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)

#Need a method to parse data
#Import tkinter and Flask
#(Probably optional for now) Add a scrapy to scrape off sites
