import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData
conn_str = 'mssql+pyodbc://LAVANYA/MINI_PROJECT?driver=ODBC+Driver+17+for+SQL+Server'
engine = create_engine(conn_str, echo=True)
metadata = MetaData()
students_table = Table('students', metadata,
                       Column('StudentID', String, primary_key=True),
                       Column('StudentName', String),
                       Column('Admission_Batch', String),
                       Column('Branch', String))

semester_table = Table('E1S1', metadata,
                       Column('StudentID', String),
                       Column('StudentName', String),
                       Column('AcademicYear', String),
                       Column('Branch', String),
                       Column('Semester', String),
                       Column('CourseCode', String),
                       Column('SubjectName', String),
                       Column('InternalMarks', Float),
                       Column('Grade', String),
                       Column('Credits', Float))
metadata.create_all(engine)
def import_data(file_path, table_name, engine):
    try:
        df = pd.read_excel(file_path)
        print(f"Data from {file_path}:")
        print(df.head())
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        print(f"Data from {file_path} successfully imported to {table_name}.")
    except Exception as e:
        print(f"Error importing data from {file_path} to {table_name}: {e}")
files_and_tables = [
    ('C:/Users/nlava/Downloads/project/students.xlsx', 'students'),
    ('C:/Users/nlava/Downloads/project/E1S1.xlsx', 'E1S1'),
    ('C:/Users/nlava/Downloads/project/E1S2.xlsx', 'E1S2'),
    ('C:/Users/nlava/Downloads/project/E2S1.xlsx', 'E2S1'),
    ('C:/Users/nlava/Downloads/project/E2S2.xlsx', 'E2S2'),
    ('C:/Users/nlava/Downloads/project/E3S1.xlsx', 'E3S1'),
    ('C:/Users/nlava/Downloads/project/E3S2.xlsx', 'E3S2'),
    ('C:/Users/nlava/Downloads/project/rem1.xlsx', 'rem1'),
     ('C:/Users/nlava/Downloads/project/rem1.xlsx', 'rem2')
]
for file_path, table_name in files_and_tables:
    import_data(file_path, table_name, engine)
