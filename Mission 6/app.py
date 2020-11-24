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
        asset_id = request.form['asset_id']

        # check if asset_id is valid
        query = """
        SELECT AssetID
        FROM Instrument
        """
        db = sqlite3.connect("band.db")
        cursor = db.execute(query)
        temp = cursor.fetchall()
        cursor.close()
        db.close()
        valid_asset_ids = []
        for row in temp:
            valid_asset_ids.append(row[0])

        if asset_id not in valid_asset_ids:
            return render_template("search/search_instrument_POST.html", valid=False)
        else:
            # valid asset_id
            # instrument info
            query = """
            SELECT *
            FROM Instrument
            WHERE AssetID = ?
            """
            db = sqlite3.connect("band.db")
            cursor = db.execute(query, (asset_id,))
            instru_info = cursor.fetchone()
            cursor.close()
            db.close()

            # ownership info
            query = """
            SELECT StudentInstrument.MatricNo
            FROM StudentInstrument
            WHERE AssetID = ?
            """
            db = sqlite3.connect("band.db")
            cursor = db.execute(query, (asset_id,))
            ownership_info = cursor.fetchone()
            cursor.close()
            db.close()
            if ownership_info == None:
                # instru does not have an attached owner
                owned = False
            else:
                owned = True
                query = """
                SELECT StudentInstrument.MatricNo, Student.Name, Student.Class
                FROM StudentInstrument, Student
                WHERE StudentInstrument.MatricNo = Student.MatricNo
                AND AssetID = ?
                """
                db = sqlite3.connect("band.db")
                cursor = db.execute(query, (asset_id,))
                ownership_info = cursor.fetchone()
                cursor.close()
                db.close()

            # repair records
            # TBC

            # loan records
            query = """
            SELECT LoanNo, MatricNo, OutDate, InDate
            FROM Loan
            WHERE AssetID = ?
            ORDER BY InDate
            ORDER BY LoanNo
            """
            db = sqlite3.connect("band.db")
            cursor = db.execute(query, (asset_id,))
            loan_info = cursor.fetchall()
            cursor.close()
            db.close()
            
            return render_template("search/search_instrument_POST.html", asset_id=asset_id, valid=True,\
                 instru_info=instru_info, owned=owned, ownership_info=ownership_info, loan_info=loan_info)

@app.route("/search/student/", methods=["GET", "POST"])
def search_student():
    if request.method == "GET":
        return render_template("search/search_student_GET.html")
    else:
        matric_no = request.form['matric_no']

        # check if matric_no is valid
        query = """
        SELECT MatricNo
        FROM Student
        """
        db = sqlite3.connect("band.db")
        cursor = db.execute(query)
        temp = cursor.fetchall()
        cursor.close()
        db.close()

        valid_matric_nos = []
        for row in temp:
            valid_matric_nos.append(row[0])
        
        if matric_no not in valid_matric_nos:
            return render_template("search/search_student_POST.html", valid=False)
        else:
            # valid matric_no
            # student info
            query = """
            SELECT * 
            FROM Student
            WHERE MatricNo = ?
            """
            db = sqlite3.connect("band.db")
            cursor = db.execute(query, (matric_no,))
            student_info = cursor.fetchone()
            cursor.close()
            db.close()

            # ownership info
            query = """
            SELECT StudentInstrument.AssetID
            FROM StudentInstrument
            WHERE MatricNo = ?
            """
            db = sqlite3.connect("band.db")
            cursor = db.execute(query, (matric_no,))
            ownership_info = cursor.fetchone()
            cursor.close()
            db.close()

            if ownership_info == None:
                # instru does not have an attached owner
                owned = False
            else:
                owned = True
                query = """
                SELECT StudentInstrument.AssetID, Instrument.InstruSN, Instrument.Model, Instrument.Status
                FROM StudentInstrument, Instrument
                WHERE StudentInstrument.AssetID = Instrument.AssetID
                AND StudentInstrument.MatricNo = ?
                """
                db = sqlite3.connect("band.db")
                cursor = db.execute(query, (matric_no,))
                ownership_info = cursor.fetchall()
                cursor.close()
                db.close()

            # loan log
            query = """
            SELECT LoanNo, AssetID, OutDate, InDate
            FROM Loan
            WHERE MatricNo = ?
            ORDER BY InDate
            ORDER BY LoanNo
            """
            db = sqlite3.connect("band.db")
            cursor = db.execute(query, (matric_no,))
            loan_info = cursor.fetchall()
            cursor.close()
            db.close()

            return render_template("search/search_student_POST.html", matric_no=matric_no, valid=True,\
                student_info=student_info, owned=owned, ownership_info=ownership_info, loan_info=loan_info)

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