import pandas as pd
import pyodbc
def get_db_connection():
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAVANYA;DATABASE=MINI_PROJECT;Trusted_Connection=yes;')
    return conn
def check_password_generated(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM students WHERE StudentID = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None  # Return True if a password exists for the student

def generate_password(length=5):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def update_student_passwords():
    conn = get_db_connection()
    cursor = conn.cursor()

    df = pd.read_excel('students.xlsx')
    
    if len(df) >= 39:
        for i in range(39):
            student_id = df.at[i, 'StudentID']
            
            # Check if a password is already generated for this student
            if not check_password_generated(student_id):
                password = generate_password()
                
                # Update the password in the database
                cursor.execute("UPDATE students SET password = ? WHERE StudentID = ?", (password, student_id))
                
                # Update the password in the DataFrame
                df.at[i, 'password'] = password
        
        conn.commit()
        
        # Save the updated Excel file
        try:
            df.to_excel('students.xlsx', index=False)
            print("Passwords updated successfully in both Excel and database.")
        except PermissionError:
            print("Error: Permission denied. Please close 'students.xlsx' if it's open in another program and try again.")
        finally:
            conn.close()
    else:
        print("Not enough students in the Excel file.")

# Run the function to update passwords
update_student_passwords()
