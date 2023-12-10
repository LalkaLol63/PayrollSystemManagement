from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from auth import authenticate
from datetime import datetime
import os
import psycopg2


app = Flask(__name__)
app.secret_key = os.urandom(24)

def connect_to_db():
    conn = psycopg2.connect(
        host='127.0.0.1',
        database='postgres',
        user='postgres',
        password='uuuuu'
    )
    return conn

# Підключення через Docker
# def connect_to_db():
#     conn = psycopg2.connect(
#         dbname='postgres',
#         user='postgres',
#         password='postgres',
#         host='localhost',
#         port='5432'
#     )
#     return conn
#

# def create_tables():
#     try:
#         conn = connect_to_db()
#         cursor = conn.cursor()
#
#         # Execute SQL commands to create tables
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS Departments3 (
#                 department_id SERIAL PRIMARY KEY,
#                 department_name VARCHAR(50) NOT NULL
#             )
#         """)
#
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS Employees3 (
#                 employee_id SERIAL PRIMARY KEY,
#                 department_id INT REFERENCES Departments3(department_id),
#                 name VARCHAR(100) NOT NULL,
#                 monthly_salary DECIMAL(10, 2),
#                 year_of_birth INT,
#                 date_of_employment DATE,
#                 marital_status VARCHAR(20),
#                 gender VARCHAR(10),
#                 number_of_children INT,
#                 work_experience INT
#             )
#         """)
#
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS Sick_Leaves3 (
#                 sick_leave_id SERIAL PRIMARY KEY,
#                 employee_id INT REFERENCES Employees3(employee_id),
#                 start_date DATE,
#                 end_date DATE,
#                 duration INT,
#                 sick_leave_percentage DECIMAL(4, 2)
#             )
#         """)
#
#         # Commit changes and close connection
#         conn.commit()
#         cursor.close()
#         conn.close()
#
#         print("Tables created successfully!")
#
#     except psycopg2.Error as e:
#         print("Error creating tables:", e)
#
# def insert():
#     try:
#         conn = connect_to_db()
#         cursor = conn.cursor()
#
#         # Insert values into the Departments2 table first
#         cursor.execute("""
#             INSERT INTO Departments3 (department_name)
#             VALUES ('Engineering'), ('Management')
#             RETURNING department_id  -- Return the department_id values after insertion
#         """)
#
#         department_ids = cursor.fetchall()  # Fetch the department_id values
#         department_ids = [d[0] for d in department_ids]  # Extract the IDs from the result
#
#         # Now insert values into the Employees2 table using the obtained department_ids
#         cursor.execute("""
#             INSERT INTO Employees3 (department_id, name, monthly_salary, year_of_birth, date_of_employment, marital_status, gender, number_of_children, work_experience)
#             VALUES
#                 (%s, 'John Doe', 3500.00, 1985, '2020-07-15', 'Married', 'Male', 2, 5),
#                 (%s, 'Alice Smith', 4200.50, 1990, '2018-04-20', 'Single', 'Female', 0, 8),
#                 (%s, 'Emma Johnson', 3000.75, 1988, '2019-11-10', 'Married', 'Female', 1, 6);
#         """, (department_ids[0], department_ids[0], department_ids[0]))  # Use the obtained IDs
#
#         # Commit changes for Employees2 table insertion
#         conn.commit()
#
#         # Close connection
#         cursor.close()
#         conn.close()
#
#         print("Inserted successfully!")
#
#     except psycopg2.Error as e:
#         print("Error inserting:", e)
#
#
#
# def select():
#     try:
#         conn = connect_to_db()
#         cursor = conn.cursor()
#         cursor.execute("""
#             SELECT * FROM Employees3
#         """)
#
#         # Fetch all rows from the executed query
#         employees_data = cursor.fetchall()
#
#         # Print fetched data
#         for employee in employees_data:
#             print(employee)
#
#         # Close connection
#         cursor.close()
#         conn.close()
#
#         print("Selection successful!")  # Indicate that the selection process is completed
#
#     except psycopg2.Error as e:
#         print("Error selecting:", e)
#
# select()


@app.route('/')  # Головна сторінка
def index():
    return render_template('login.html')

# Login route for administrators
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):

            return redirect(url_for('employees'))
        else:
            error = "Invalid credentials. Please try again."
            return render_template('error.html')
    return render_template('login.html', error=error)

@app.route('/temp', methods=['GET', 'POST'])
def temp():
    return render_template('login.html')
    return redirect(url_for('employees'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    return redirect(url_for('employees'))

@app.route('/employees', methods=['GET', 'POST'])
def employees():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Employees3 ORDER BY date_of_employment DESC;")  # Modify query as needed
        employees_data = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('employees.html', employees_data=employees_data)
    except psycopg2.Error as e:
        print("Error fetching data:", e)


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    try:
        if request.method == 'POST':
            # Retrieve form data
            department_id = int(request.form['department_id'])
            name = request.form['name']
            monthly_salary = float(request.form['monthly_salary'])
            year_of_birth = int(request.form['year_of_birth'])
            date_of_employment = request.form['date_of_employment']
            marital_status = request.form['marital_status']
            gender = request.form['gender']
            number_of_children = request.form['number_of_children']


            conn = connect_to_db()
            cursor = conn.cursor()

            cursor.execute("""
                           INSERT INTO Employees3 (department_id, name, monthly_salary, year_of_birth, date_of_employment, marital_status, gender, number_of_children)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                       """, (
            department_id, name, monthly_salary, year_of_birth, date_of_employment, marital_status, gender,
            number_of_children))
            conn.commit()

            cursor.close()
            conn.close()

            flash('Employee added successfully!', 'success')
            return redirect(url_for('employees'))

    except Exception as e:
        flash('Failed to add employee. Please try again.', 'error')
        return redirect(url_for('employees'))



@app.route('/delete_employee/<employee_id>', methods=['POST', 'DELETE'])
def delete_employee(employee_id):
    if request.method == 'POST' or request.method == 'DELETE':
        try:
            conn = connect_to_db()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM Employees3 WHERE id = 162", (employee_id,))

            conn.commit()

            cursor.close()
            conn.close()

            flash('Employee deleted successfully!', 'success')
            return redirect(url_for('employees'))

        except Exception as e:
            flash('Failed to delete employee. Please try again.', 'error')
            return redirect(url_for('employees'))


@app.route('/show_add_employee_form')
def show_add_employee_form():
    return render_template('add_employee.html')


@app.route('/add_sick_leave', methods=['POST', 'GET'])
def add_sick_leave():
    try:
        if request.method == 'POST':
            # Retrieve form data
            employee_id = int(request.form['employee_id'])
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            duration = int(request.form['duration'])
            sick_leave_percentage = float(request.form['sick_leave_percentage'])

            conn = connect_to_db()
            cursor = conn.cursor()

            cursor.execute("""
                           INSERT INTO Sick_Leaves (employee_id, start_date, end_date, duration, sick_leave_percentage)
                           VALUES (%s, %s, %s, %s, %s)
                       """, (employee_id, start_date, end_date, duration, sick_leave_percentage))

            conn.commit()

            cursor.close()
            conn.close()

            flash('Sick leave added successfully!', 'success')
            return redirect(url_for('add_sick_leave'))
            return render_template('seak_leave.html')


    except Exception as e:
        flash('Failed to add sick leave. Please try again.', 'error')
        return redirect(url_for('add_sick_leave'))

@app.route('/retirement')
def retirement():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT employee_id, department_id, name, monthly_salary, year_of_birth, date_of_employment, marital_status, gender, number_of_children, work_experience
FROM Employees3 WHERE year_of_birth < 1989;

        """)
        employees_data = cursor.fetchall()
        print(employees_data)
        print(employees_data)

        cursor.close()
        conn.close()

        return render_template('employees.html', employees_data=employees_data)

    except psycopg2.Error as e:
        print("Error fetching retirement age employees:", e)

@app.route('/salary_less_than_n', methods=['POST', 'GET'])
def salary_less_than_n():
    if request.method == 'POST':
        try:
            salary_threshold = float(request.form['salary_threshold'])

            conn = connect_to_db()
            cursor = conn.cursor()

            cursor.execute("""
               SELECT *
                FROM Employees3
                WHERE monthly_salary < %s
                ORDER BY department_id
            """, (salary_threshold,))

            filtered_employees_data = cursor.fetchall()

            cursor.close()
            conn.close()

            return render_template('employees.html', employees_data=filtered_employees_data)

        except psycopg2.Error as e:
            print("Error fetching employees with salary less than threshold:", e)

    return render_template('employees.html')  # Render the default employees page for GET requests


@app.route('/average_salaries')
def average_salaries():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Fetch average salaries per department for males and females separately
        cursor.execute("""
            SELECT department_id, gender, AVG(monthly_salary) AS avg_salary
            FROM Employees3
            GROUP BY department_id, gender
        """)
        department_gender_avg_salaries = {}
        for row in cursor.fetchall():
            department_id, gender, avg_salary = row
            department_gender_avg_salaries.setdefault(department_id, {'Male': 0.0, 'Female': 0.0})[gender] = avg_salary

        # Fetch overall average salaries for males and females
        cursor.execute("""
            SELECT gender, AVG(monthly_salary) AS avg_salary
            FROM Employees3
            GROUP BY gender
        """)
        overall_gender_avg_salaries = dict(cursor.fetchall())

        # Fetch overall average salaries for all women and all men
        cursor.execute("""
            SELECT gender, AVG(monthly_salary) AS avg_salary
            FROM Employees3
            GROUP BY gender
        """)
        overall_avg_salaries = dict(cursor.fetchall())

        cursor.close()
        conn.close()

        return render_template('average_salaries.html',
                               department_gender_avg_salaries=department_gender_avg_salaries,
                               overall_gender_avg_salaries=overall_gender_avg_salaries,
                               overall_avg_salaries=overall_avg_salaries)

    except psycopg2.Error as e:
        print("Error fetching average salaries:", e)
        flash("Error fetching average salaries. Please try again.", 'error')
        return render_template('average_salaries.html',
                               department_gender_avg_salaries={},
                               overall_gender_avg_salaries={},
                               overall_avg_salaries={})


@app.route('/average_age')
def average_age():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        current_year = datetime.now().year
        # Query to fetch average salaries per department for males and females separately
        cursor.execute("""
            SELECT department_id, gender, AVG(%s - year_of_birth) AS avg_age
            FROM Employees
            GROUP BY department_id, gender
        """)
        department_gender_avg_age = {}
        for row in cursor.fetchall():
            department_id = row[0]
            gender = row[1]
            avg_salary = row[2]

            if department_id not in department_gender_avg_age:
                department_gender_avg_age[department_id] = {'Male': 0.0, 'Female': 0.0}

            department_gender_avg_age[department_id][gender] = avg_salary

        # Query to fetch overall average salaries for males and females
        cursor.execute("""
            SELECT gender, AVG(%s - year_of_birth) AS avg_age
            FROM Employees
            GROUP BY gender
        """)
        overall_gender_avg_age = dict(cursor.fetchall())

        # Query to fetch overall average salaries for all women and all men
        cursor.execute("""
            SELECT gender, AVG(%s - year_of_birth) AS avg_age
            FROM Employees
            GROUP BY gender
        """)
        overall_avg_age = dict(cursor.fetchall())

        cursor.close()
        conn.close()

        return render_template('average_age.html',
                               department_gender_avg_age=department_gender_avg_age,
                               overall_gender_avg_age=overall_gender_avg_age,
                               overall_avg_age=overall_avg_age)

    except psycopg2.Error as e:
        print("Error fetching average salaries:", e)
        return render_template('average_age.html',
                               department_gender_avg_age={},
                               overall_gender_avg_age={},
                               overall_avg_age={})


@app.route('/average_experience')
def average_experience():
    current_year = datetime.now().year
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Query to fetch average experience per department and overall average experience
        cursor.execute("""
            SELECT department_id, AVG(%s - EXTRACT(YEAR FROM date_of_employment)) AS avg_experience
            FROM Employees3
            GROUP BY department_id
        """, (current_year,))
        department_avg_experience = {row[0]: row[1] for row in cursor.fetchall()}

        # Query to calculate overall average experience for the company
        cursor.execute("""
            SELECT AVG(%s - EXTRACT(YEAR FROM date_of_employment)) AS overall_avg_experience
            FROM Employees3
        """, (current_year,))
        overall_avg_experience = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return render_template('average_experience.html',
                               department_avg_experience=department_avg_experience,
                               overall_avg_experience=overall_avg_experience)

    except psycopg2.Error as e:
        print("Error fetching average experience:", e)
        return render_template('average_experience.html',
                               department_avg_experience={},
                               overall_avg_experience=0.0)




@app.route('/seak_leaves', methods=['GET', 'POST'])
def seak_leaves():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Seak_Leaves")
        seak_leaves_data = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('seak_leaves.html', seak_leaves_data=seak_leaves_data)
    except psycopg2.Error as e:
        print("Error fetching data:", e)

@app.route('/add_seak_leaves', methods=['GET', 'POST'])
def add_seak_leaves():
    try:
        if request.method == 'POST':
            # Retrieve form data
            employee_id = int(request.form['employee_id'])
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            duration = int(request.form['duration'])
            sick_leave_percentage = float(request.form['sick_leave_percentage'])

            conn = connect_to_db()
            cursor = conn.cursor()

            cursor.execute("""
                           INSERT INTO Sick_Leaves (employee_id, start_date, end_date, duration, sick_leave_percentage)
                           VALUES (%s, %s, %s, %s, %s)
                       """, (employee_id, start_date, end_date, duration, sick_leave_percentage))
            conn.commit()

            cursor.close()
            conn.close()

            flash('Employee added successfully!', 'success')
            return redirect(url_for('show_seak_leave_form'))

    except Exception as e:
        flash('Failed to add employee. Please try again.', 'error')
        return redirect(url_for('show_seak_leave_form'))


@app.route('/show_seak_leave_form')
def show_seak_leave_form():
    return render_template('seak_leaves.html')

if __name__ == '__main__':
    app.run(debug=True)
