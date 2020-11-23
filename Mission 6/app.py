from flask import Flask, render_template, url_for, request, redirect
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/display/")
def display():
    return render_template("display/display.html")

@app.route("/display/loan/")
def display_loan():
    return render_template("display/display_loan.html")

@app.route("/search/")
def search():
    return render_template("search/search.html")

@app.route("/update/")
def update():
    return render_template("update/update.html")

if __name__ == "__main__":
    app.run(debug=True)