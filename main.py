from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")  # default route
def home():
    return "Hello darkness my old friend"


if __name__ == "__main__":
    app.run(debug=True)

#Need a method to parse data
#Import tkinter and Flask
#(Probably optional for now) Add a scrapy to scrape off sites
