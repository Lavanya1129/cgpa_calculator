from flask import Flask
import pyodbc

app = Flask(__name__)

server = 'LAVANYA'  
database = 'MINI_PROJECT'
driver = '{ODBC Driver 17 for SQL Server}'
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes'
connection = pyodbc.connect(conn_str)
cursor = connection.cursor()

grade_points = {'EX': 10, 'A': 9, 'B': 8, 'C': 7, 'D': 6, 'E': 5, 'R': 0}

def calculate_sgpa(student_id, semester_table):
    cursor.execute(f"SELECT Grade, Credits FROM {semester_table} WHERE StudentID = ?", student_id)
    rows = cursor.fetchall()
    total_credits = 0
    total_grade_points = 0
    for row in rows:
        grade = row.Grade
        credits = row.Credits
        total_credits += credits
        total_grade_points += grade_points.get(grade, 0) * credits
    if total_credits == 0:
        return 0.0  
    sgpa = total_grade_points / total_credits
    return round(sgpa, 2)


def update_all_students_cgpa():
    cursor.execute('SELECT DISTINCT StudentID FROM CGPAResults')
    student_ids = cursor.fetchall()
    
    for student_id_tuple in student_ids:
        student_id = student_id_tuple[0]  
        
        # Fetch SGPA values for the student
        cursor.execute(f"SELECT E1S1_SGPA, E1S2_SGPA, E2S1_SGPA, E2S2_SGPA, E3S1_SGPA, E3S2_SGPA FROM CGPAResults WHERE StudentID = ?", student_id)
        sgpa_rows = cursor.fetchone()

        if sgpa_rows:
            sgpa_values = list(sgpa_rows)
            total_sgpa = sum(sgpa_values)
            cgpa = round(total_sgpa / len(sgpa_values), 2)  # Round CGPA to 2 decimal places
        
            cursor.execute(f"UPDATE CGPAResults SET CGPA = ? WHERE StudentID = ?", (cgpa, student_id))
            connection.commit()

if __name__ == '__main__':
    update_all_students_cgpa()

    cursor.close()
    connection.close()

