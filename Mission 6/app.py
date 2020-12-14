from flask import Flask, render_template, url_for, request, redirect
import sqlite3

####################
# HELPER FUNCTIONS #
####################

def valid_asset_id(asset_id):
    # check if asset ID is valid, returns True/False
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

    return (asset_id in valid_asset_ids)

def valid_matric_no(matric_no):
    # check if matric no is valid, returns True/False
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

    return (matric_no in valid_matric_nos)

def valid_loan_no(loan_no):
    # check if loan no is valid for loan returns, returns True/False
    query = """
    SELECT LoanNo
    FROM Loan
    WHERE InDate IS NULL
    """
    db = sqlite3.connect("band.db")
    cursor = db.execute(query)
    temp = cursor.fetchall()
    cursor.close()
    db.close()

    valid_loan_nos = []
    for row in temp:
        valid_loan_nos.append(str(row[0]))
    
    return (loan_no in valid_loan_nos)

###########
# WEB APP #
###########
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/display_loan/")
def display_loan():
    query = """
    SELECT Loan.LoanNo, Loan.MatricNo, Student.Name, Student.Class, Loan.AssetID, Instrument.InstruSN, Instrument.Section, Loan.OutDate, Loan.InDate
    FROM Loan, Student, Instrument
    WHERE Loan.MatricNo = Student.MatricNo
    AND Loan.AssetID = Instrument.AssetID
    ORDER BY Loan.InDate
    AND Loan.LoanNo
    """

    db = sqlite3.connect("band.db")
    cursor = db.execute(query)
    loan_data = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("display/display_loan.html", loan_data=loan_data)

@app.route("/display_stock/")
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

@app.route("/display_student/")
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

@app.route("/search_instrument/", methods=["GET", "POST"])
def search_instrument():
    if request.method == "GET":
        return render_template("search/search_instrument_GET.html")
    else:
        asset_id = request.form['asset_id']

        if not valid_asset_id(asset_id):
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
            if ownership_info[0] == None:
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

            # loan records
            query = """
            SELECT LoanNo, MatricNo, OutDate, InDate
            FROM Loan
            WHERE AssetID = ?
            ORDER BY InDate
            AND LoanNo
            """
            db = sqlite3.connect("band.db")
            cursor = db.execute(query, (asset_id,))
            loan_info = cursor.fetchall()
            cursor.close()
            db.close()
            
            return render_template("search/search_instrument_POST.html", asset_id=asset_id, valid=True,\
                 instru_info=instru_info, owned=owned, ownership_info=ownership_info, loan_info=loan_info)

@app.route("/search_student/", methods=["GET", "POST"])
def search_student():
    if request.method == "GET":
        return render_template("search/search_student_GET.html")
    else:
        matric_no = request.form['matric_no']

        if not valid_matric_no(matric_no):
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
            AND LoanNo
            """
            db = sqlite3.connect("band.db")
            cursor = db.execute(query, (matric_no,))
            loan_info = cursor.fetchall()
            cursor.close()
            db.close()

            return render_template("search/search_student_POST.html", matric_no=matric_no, valid=True,\
                student_info=student_info, owned=owned, ownership_info=ownership_info, loan_info=loan_info)

@app.route("/update_instrument/", methods=["GET", "POST"])
def update_instrument():
    if request.method == "GET":
        return render_template("update/update_instrument_GET.html")
    else:
        asset_id, remarks, status = request.form['asset_id'], request.form['remarks'], request.form['status']
        
        if not valid_asset_id(asset_id):
            return render_template("update/update_instrument_POST.html", valid=False)
        else:
            if remarks == "":
                query = """
                UPDATE Instrument Set Remarks = NULL, Status = ?
                WHERE AssetID = ?
                """
                db = sqlite3.connect("band.db")
                db.execute(query, (status, asset_id))
                db.commit()
                db.close()
            else:
                query = """
                UPDATE Instrument Set Remarks = ?, Status = ?
                WHERE AssetID = ?
                """
                db = sqlite3.connect("band.db")
                db.execute(query, (remarks, status, asset_id))
                db.commit()
                db.close()

            query = """
            SELECT * 
            FROM Instrument
            WHERE AssetID = ?
            """
            db = sqlite3.connect("band.db")
            cursor = db.execute(query, (asset_id,))
            new_info = cursor.fetchone()
            cursor.close()
            db.close()

            return render_template("update/update_instrument_POST.html", asset_id=asset_id, valid=True, new_info=new_info)

@app.route("/update_loan/")
def update_loan():
    # GET method
    return render_template("update/update_loan_GET.html")

@app.route("/update_loan/out/", methods=["POST"])
def update_loan_out():
    # POST method
    matric_no, asset_id, out_date = request.form["matric_no"], request.form["asset_id"], request.form["out_date"]
    if not valid_matric_no(matric_no):
        return render_template("update/update_loan_out_POST.html", asset_id_valid=True, matric_no_valid=False,\
            valid_date=True)
    elif not valid_asset_id(asset_id):
        return render_template("update/update_loan_out_POST.html", asset_id_valid=False, matric_no_valid=True,\
            valid_date=True)
    elif out_date == "":
        return render_template("update/update_loan_out_POST.html", asset_id_valid=True, matric_no_valid=True,\
            valid_date=False)
    else:
        query = """
        INSERT INTO Loan(MatricNo, AssetID, OutDate)
        VALUES (?,?,?)
        """
        db = sqlite3.connect("band.db")
        db.execute(query, (matric_no, asset_id, out_date))
        db.commit()
        db.close()

        query = """
        UPDATE Instrument Set Status = 'Loaned'
        WHERE AssetID = ?
        """
        db = sqlite3.connect("band.db")
        db.execute(query, (asset_id,))
        db.commit()
        db.close()

        query = """
        SELECT seq
        FROM sqlite_sequence
        WHERE name = 'Loan'
        """
        db = sqlite3.connect("band.db")
        cursor = db.execute(query)
        loan_no = cursor.fetchone()
        cursor.close()
        db.close()

        return render_template("update/update_loan_out_POST.html", asset_id_valid=True, matric_no_valid=True,\
            valid_date=True, matric_no=matric_no, asset_id=asset_id, out_date=out_date, loan_no=loan_no)

@app.route("/update_loan/in/", methods=["POST"])
def update_loan_in():
    # POST method
    loan_no, in_date = request.form["loan_no"], request.form["in_date"]
    if not valid_loan_no(loan_no):
        return render_template("update/update_loan_in_POST.html", loan_no_valid=False, date_valid=True)
    elif in_date == "":
        return render_template("update/update_loan_in_POST.html", loan_no_valid=True, date_valid=False)
    else:
        query = """
        UPDATE Loan Set InDate = ?
        WHERE LoanNo = ?
        """
        db = sqlite3.connect("band.db")
        db.execute(query, (in_date, loan_no))
        db.commit()
        db.close()

        query = """
        SELECT *
        FROM Loan
        WHERE LoanNo = ?
        """
        db = sqlite3.connect("band.db")
        cursor = db.execute(query, (loan_no,))
        loan_data = cursor.fetchone()
        cursor.close()
        db.close()

        query = """
        UPDATE Instrument Set Status = 'Normal'
        WHERE AssetID = ?
        """
        db = sqlite3.connect("band.db")
        db.execute(query, (loan_data[2],))
        db.commit()
        db.close()

        print(loan_data)
        return render_template("update/update_loan_in_POST.html", loan_no_valid=True, date_valid=True, \
            loan_data=loan_data)

@app.route("/update_ownership/", methods=["GET", "POST"])
def update_ownership():
    if request.method == "GET":
        return render_template("update/update_ownership_GET.html")
    else:
        asset_id, matric_no = request.form['asset_id'], request.form['matric_no']
        print(asset_id, matric_no)

        if not valid_asset_id(asset_id):
            # invalid asset id
            return render_template("update/update_ownership_POST.html", asset_id_valid=False, matric_no_valid=True)
        else:
            if matric_no is not "" and not valid_matric_no(matric_no):
                # invalid matric no, only if the field is filled
                return render_template("update/update_ownership_POST.html", asset_id_valid=True, matric_no_valid=False)
            else:
                if matric_no == "":
                    query = """
                    UPDATE StudentInstrument Set MatricNo = NULL
                    WHERE AssetID = ?
                    """
                    db = sqlite3.connect("band.db")
                    db.execute(query, (asset_id, ))
                    db.commit()
                    db.close()
                else:
                    query = """
                    UPDATE StudentInstrument Set MatricNo = ?
                    WHERE AssetID = ?
                    """
                    db = sqlite3.connect("band.db")
                    db.execute(query, (matric_no, asset_id))
                    db.commit()
                    db.close()

                query = """
                SELECT AssetID, MatricNo
                FROM StudentInstrument
                WHERE AssetID = ?
                """
                db = sqlite3.connect("band.db")
                cursor = db.execute(query, (asset_id,))
                new_info = cursor.fetchone()
                cursor.close()
                db.close()

                return render_template("update/update_ownership_POST.html", asset_id=asset_id, matric_no=matric_no, \
                    asset_id_valid=True, matric_no_valid=True, new_info=new_info)

@app.route("/update_student/", methods=["GET", "POST"])
def update_student():
    if request.method == "GET":
        return render_template("update/update_student_GET.html")
    else:
        matric_no, class_, section, in_band = \
            request.form['matric_no'], request.form['class_'], request.form['section'], request.form['in_band']
        
        if not valid_matric_no(matric_no):
            return render_template("update/update_student_POST.html", valid=False)
        else:
            query = """
            UPDATE Student Set Class = ?, Section = ?, InBand = ?
            WHERE MatricNo = ?
            """
            db = sqlite3.connect("band.db")
            db.execute(query, (class_, section, in_band, matric_no))
            db.commit()
            db.close()

            query = """
            SELECT *
            FROM Student
            WHERE MatricNo = ?
            """
            db = sqlite3.connect("band.db")
            cursor = db.execute(query, (matric_no,))
            new_info = cursor.fetchone()
            cursor.close()
            db.close()

            return render_template("update/update_student_POST.html", valid=True, matric_no=matric_no, new_info=new_info)

if __name__ == "__main__":
    app.run(debug=True)