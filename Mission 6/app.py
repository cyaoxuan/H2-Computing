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
    query = """
    SELECT Loan.MatricNo, Student.Name, Student.Class, Loan.AssetID, Instrument.Section, Loan.OutDate
    FROM Loan, Student, Instrument
    WHERE Loan.MatricNo = Student.MatricNo
    AND Loan.AssetID = Instrument.AssetID
    AND Loan.InDate IS NULL
    """

    db = sqlite3.connect("band.db")
    cursor = db.execute(query)
    loan_data = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("display/display_loan.html", loan_data=loan_data)

@app.route("/display/repair/")
# TBC
def display_repair():
    return render_template("display/display_repair.html")

@app.route("/display/stock/")
def display_stock():
    query = """
    SELECT *
    FROM Instrument
    ORDER BY Instrument.AssetID
    """

    db = sqlite3.connect("band.db")
    cursor = db.execute(query)
    stock_data = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template("display/display_stock.html", stock_data=stock_data)

@app.route("/display/student/")
def display_student():
    query = """
    SELECT Student.MatricNo, Student.Name, Student.Class, Student.Section, Instrument.AssetID
    FROM Student, Instrument, StudentInstrument
    WHERE Student.MatricNo = StudentInstrument.MatricNo
    AND Instrument.AssetID = StudentInstrument.AssetID
    AND Student.InBand = 'Yes'
    ORDER BY Student.MatricNo
    """

    db = sqlite3.connect("band.db")
    cursor = db.execute(query)
    student_data = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("display/display_student.html", student_data=student_data)

@app.route("/search/")
def search():
    return render_template("search/search.html")

@app.route("/search/instrument/", methods=["GET", "POST"])
def search_instrument():
    if request.method == "GET":
        return render_template("search/search_instrument_GET.html")
    else:
        return render_template("search/search_instrument_POST.html")

@app.route("/search/student/", methods=["GET", "POST"])
def search_student():
    if request.method == "GET":
        return render_template("search/search_student_GET.html")
    else:
        return render_template("search/search_student_POST.html")

@app.route("/update/")
def update():
    return render_template("update/update.html")

@app.route("/update/instrument/", methods=["GET", "POST"])
def update_instrument():
    if request.method == "GET":
        return render_template("update/update_instrument_GET.html")
    else:
        return render_template("update/update_instrument_POST.html")

@app.route("/update/loan/", methods=["GET", "POST"])
def update_loan():
    if request.method == "GET":
        return render_template("update/update_loan_GET.html")
    else:
        return render_template("update/update_loan_POST.html")

@app.route("/update/ownership/", methods=["GET", "POST"])
def update_ownership():
    if request.method == "GET":
        return render_template("update/update_ownership_GET.html")
    else:
        return render_template("update/update_ownership_POST.html")

@app.route("/update/repair/", methods=["GET", "POST"])
def update_repair():
    if request.method == "GET":
        return render_template("update/update_repair_GET.html")
    else:
        return render_template("update/update_repair_POST.html")

@app.route("/update/student/", methods=["GET", "POST"])
def update_student():
    if request.method == "GET":
        return render_template("update/update_student_GET.html")
    else:
        return render_template("update/update_student_POST.html")

if __name__ == "__main__":
    app.run(debug=True)