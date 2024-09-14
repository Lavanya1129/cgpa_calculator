import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
import pyodbc
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = '12345'  



app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'nlavanya1129@gmail.com'
app.config['MAIL_PASSWORD'] = 'yducbyigrhplcwby'
app.config['MAIL_DEFAULT_SENDER'] = 'nlavanya1129@gmail.com'

mail = Mail(app) 

def get_db_connection():
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAVANYA;DATABASE=MINI_PROJECT;Trusted_Connection=yes;')
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/student/retrieve_password', methods=['GET', 'POST'])
def retrieve_password():
    if request.method == 'POST':
        student_id = request.form.get('StudentID')
        student_email = request.form.get('email')

        if not student_id or not student_email:
            return render_template('retrieve_password.html', error="Missing Student ID or Email")
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE students SET Email = ? WHERE StudentID = ?", (student_email, student_id))
            conn.commit()
            cursor.execute("SELECT password FROM students WHERE StudentID = ?", (student_id,))
            student_data = cursor.fetchone()

            if student_data:
                retrieved_password = student_data.password
                send_password_email(retrieved_password, student_email)
                session['retrieved_password'] = retrieved_password
                return redirect(url_for('student_login'))
            else:
                return render_template('retrieve_password.html', error="Student not found")
        except pyodbc.Error as e:
            conn.rollback() 
            print(f"Pyodbc error during password retrieval: {str(e)}")
            return render_template('retrieve_password.html', error="An error occurred during password retrieval.")
        finally:
            conn.close()
    return render_template('retrieve_password.html')

def send_password_email(password, recipient_email):
    login_link = url_for('student_login', _external=True)
    msg = Message('Password Retrieval', recipients=[recipient_email])
    msg.body = f"Your password is: {password}\n\nLogin here: {login_link}"
    mail.send(msg)
 
@app.route('/student/login', methods=['GET','POST'])
def student_login():
    if request.method == 'POST':
        student_id = request.form.get('StudentID')
        password = request.form.get('password')
        if not student_id or not password:
            return render_template('student_login.html', error="Missing StudentID or password")
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT StudentName, Branch, Admission_Batch, password FROM Students WHERE StudentID = ?", (student_id,))
            row = cursor.fetchone()
            if row:
                db_password = row.password  
                if db_password == password:
                    session['StudentID'] = student_id
                    session['StudentName'] = row.StudentName
                    session['Branch'] = row.Branch
                    session['Admission_Batch'] = row.Admission_Batch
                    return redirect(url_for('student_dashboard'))
                else:
                    return render_template('student_login.html', error="Invalid credentials")
            else:
                return render_template('student_login.html', error="Student not found")
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return render_template('student_login.html', error="An error occurred during login.")
        finally:
            conn.close()
    return render_template('student_login.html')
@app.route('/student/dashboard')
def student_dashboard():
    if 'StudentID' not in session:
        return redirect(url_for('student_login'))
    student_id = session.get('StudentID')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT StudentID, StudentName, Batch, Branch, CGPA FROM CGPAResults WHERE StudentID = ?", (student_id,))
        student_data = cursor.fetchone()
    except Exception as e:
        student_data = None
    finally:
        conn.close()
    return render_template('student_dashboard.html', student_data=student_data)
@app.route('/faculty/login', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        faculty_id = request.form['faculty_id']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM Faculty WHERE FacultyID = ?", (faculty_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0] == password:
            session['FacultyID'] = faculty_id
            return redirect(url_for('faculty_dashboard'))
        else:
            return render_template('faculty_login.html', error="Invalid username or password")
    return render_template('faculty_login.html')
@app.route('/faculty/dashboard')
def faculty_dashboard():
    if 'FacultyID' not in session:
        return redirect(url_for('faculty_login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM CGPAResults")
        students = cursor.fetchall()
    except Exception as e:
        students = []
    finally:
        conn.close()

    return render_template('faculty_dashboard.html', students=students)

@app.route('/faculty/register', methods=['GET', 'POST'])
def faculty_register():
    if request.method == 'POST':
        faculty_id = request.form['faculty_id']
        faculty_name=request.form['FacultyName']
        email=request.form['Email']
        department=request.form['Department']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO Faculty (FacultyID,FacultyName,Email,Department,password) VALUES (?, ?,?,?,?)", (faculty_id,faculty_name,email,department,password,))
            conn.commit()
        except Exception as e:
            conn.rollback()
        finally:
            conn.close()

    return render_template('faculty_register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.route('/faculty/download')
def download_csv():
    if 'FacultyID' not in session:
        return redirect(url_for('faculty_login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM CGPAResults")
        students = cursor.fetchall()
        
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['Student ID', 'Student Name', 'Branch', 'Batch', 'E1S1_SGPA','E1S2_SGPA','E2S1_SGPA','E2S2_SGPA','E3S1_SGPA','E3S2_SGPA','CGPA'])
    
        for student in students:
            writer.writerow([student.StudentID, student.StudentName, student.Branch, student.Batch,student.E1S1_SGPA,student.E1S2_SGPA,student.E2S1_SGPA,student.E2S2_SGPA,student.E3S1_SGPA,student.E3S2_SGPA, student.CGPA])
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=students_cgpa.csv"
        response.headers["Content-type"] = "text/csv"
        return response
    except Exception as e:
        print(f"Error during CSV generation: {str(e)}")
        return jsonify({'error': 'Failed to generate CSV'}), 500
    
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)





