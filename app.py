from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    flash,
    session,
    g,
)
from datetime import datetime
import os
import psycopg2
from CompanyDB import CompanyDB
import redis
from auth import Authentication
from forms import *
from managers.EmployeeManager import EmployeeManager
from managers.SickLeaveManager import SickLeaveManager
from models import Employee, SickLeave

app = Flask(__name__)
app.secret_key = os.urandom(24)
sql_dbase = None
employee_manager = None
sick_leave_manager = None
auth = Authentication()


def connect_to_sql_db():
    conn = psycopg2.connect(
        dbname="payrollsystemdb",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432",
    )
    return conn


def connect_to_redis_db():
    redis_cli = redis.Redis(host="localhost", port=6379, db=0, password="secretpass")
    return redis_cli


def get_sql_db():
    """Соединение с БД, если оно еще не установлено"""
    if not hasattr(g, "link_db"):
        g.link_sql_db = connect_to_sql_db()
    return g.link_sql_db


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global employee_manager
    global sick_leave_manager
    db = get_sql_db()
    employee_manager = EmployeeManager(db)
    sick_leave_manager = SickLeaveManager(db)


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установлено"""
    if hasattr(g, "link_db"):
        g.link_db.close()


@app.context_processor
def inject_sick_leave_count():
    sick_leave_count = sick_leave_manager.get_total_pending_sick_leaves()
    return dict(
        sick_leave_count=sick_leave_count, current_user=auth.get_current_user_role()
    )


def create_tables():
    try:
        conn = connect_to_sql_db()
        cursor = conn.cursor()

        # Execute SQL commands to create tables
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Departments3 (
                department_id SERIAL PRIMARY KEY,
                department_name VARCHAR(50) NOT NULL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Employees3 (
                employee_id SERIAL PRIMARY KEY,
                department_id INT REFERENCES Departments3(department_id),
                name VARCHAR(100) NOT NULL,
                monthly_salary DECIMAL(10, 2),
                year_of_birth INT,
                date_of_employment DATE,
                marital_status VARCHAR(20),
                gender VARCHAR(10),
                number_of_children INT,
                work_experience INT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Sick_Leaves3 (
                sick_leave_id SERIAL PRIMARY KEY,
                employee_id INT REFERENCES Employees3(employee_id),
                start_date DATE,
                end_date DATE,
                duration INT,
            )
        """
        )

        # Commit changes and close connection
        conn.commit()
        cursor.close()
        conn.close()

        print("Tables created successfully!")

    except psycopg2.Error as e:
        print("Error creating tables:", e)


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_id = login_form.login.data
        password = login_form.password.data
        remember = login_form.remember.data
        print(user_id, password)
        if auth.authenticate(user_id, password, remember):
            user_data = auth.get_user_data(user_id)
            if user_data.get("role") == "admin":
                return redirect(url_for("employees"))
            else:
                return redirect(url_for("profile", employee_id=user_id))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", form=login_form)


@app.route("/logout", methods=["GET"])
def logout():
    auth.logout_user()
    return redirect("login")


@app.route("/profile/<employee_id>", methods=["GET", "POST"])
@auth.employee_login_required
def profile(employee_id):
    add_sick_leave_form = SickLeaveForm(employee_id=employee_id)
    if add_sick_leave_form.validate_on_submit():
        print("we are here!")
        new_sick_leave_status = (
            "Pending" if auth.get_current_user_role() == "employee" else "Approved"
        )
        res = sick_leave_manager.add_new_sick_leave(
            new_sick_leave=SickLeave(
                add_sick_leave_form.employee_id.data,
                add_sick_leave_form.start_date.data,
                add_sick_leave_form.end_date.data,
                new_sick_leave_status,
            )
        )
        if not res:
            flash("Failed to add sick leave. Please try again.", "danger")
        else:
            flash("Sick leave added successfully!", "success")
            return redirect(url_for("profile", employee_id=employee_id))

    employee_data = employee_manager.get_employee_by_id(employee_id)
    if not employee_data:
        flash(f"There's no profile with an id {employee_id}.", "danger")
        return redirect(url_for("employees"))
    else:
        employee = employee_data[0]
        employee_month_sick_leaves = (
            sick_leave_manager.get_all_sick_leaves_in_current_month_by_employee(
                employee_id=employee_id
            )
        )
        employee.calculate_current_month_sick_leaves_duration(
            employee_month_sick_leaves
        )
        employee.calculate_adjusted_salary()

        employee_approved_sick_leaves = (
            sick_leave_manager.get_all_sick_leaves_by_employee(employee_id=employee_id)
        )
        employee_pending_sick_leaves = (
            sick_leave_manager.get_all_sick_leaves_by_employee(
                employee_id=employee_id, status="Pending"
            )
        )
        return render_template(
            "profile.html",
            employee=employee,
            pending_sick_leaves_data=employee_pending_sick_leaves,
            approved_sick_leaves_data=employee_approved_sick_leaves,
            add_sick_leave_form=add_sick_leave_form,
        )


@app.route("/home", methods=["GET", "POST"])
def home():
    return redirect(url_for("employees"))


@app.route("/employees", methods=["GET", "POST"])
@auth.admin_login_required
def employees():
    employees_data = employee_manager.get_all_employees()
    return render_template("employees.html", employees_data=employees_data)


@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():
    add_employee_form = EmployeeForm()
    if add_employee_form.validate_on_submit():
        new_employee_id = employee_manager.add_new_employee(
            new_employee=Employee(
                add_employee_form.department_id.data,
                add_employee_form.name.data,
                add_employee_form.monthly_salary.data,
                add_employee_form.date_of_birth.data,
                add_employee_form.date_of_employment.data,
                add_employee_form.marital_status.data,
                add_employee_form.gender.data,
                add_employee_form.number_of_children.data,
            )
        )
        if not new_employee_id:
            flash("Failed to add employee. Please try again.", "danger")
        else:
            auth.add_user(new_employee_id, add_employee_form.data["password"])
            flash("Employee added successfully!", "success")
    return render_template("add_employee.html", add_employee_form=add_employee_form)


@app.route("/search_employee", methods=["POST"])
def search_employee():
    search_info = request.form["search_id_or_name"]
    try:
        search_info = int(request.form["search_id_or_name"])
        search_results = employee_manager.get_employee_by_id(search_info)
    except ValueError:
        search_results = employee_manager.get_employee_by_name(search_info)

    if not search_results:
        flash("Nothing was found.", "dark")
        return redirect(url_for("employees"))
    return render_template("employees.html", employees_data=search_results)


@app.route("/delete_employee/<employee_id>", methods=["POST"])
def delete_employee(employee_id):
    res = employee_manager.delete_employee(employee_id_to_delete=employee_id)
    if not res:
        flash("Failed to delete employee. Please try again.", "error")
    else:
        auth.delete_user(employee_id)
        flash("Employee deleted successfully!", "success")
    return redirect(url_for("employees"))


@app.route("/employees_adjusted_salaries", methods=["GET"])
def employees_adjusted_salaries():
    employees_list = employee_manager.get_all_employees()
    for employee in employees_list:
        employee_month_sick_leaves = (
            sick_leave_manager.get_all_sick_leaves_in_current_month_by_employee(
                employee_id=employee.employee_id
            )
        )
        employee.calculate_current_month_sick_leaves_duration(
            employee_month_sick_leaves
        )
        employee.calculate_adjusted_salary()
        print(employee.adjusted_salary, employee.current_month_sick_leaves_duration)
        print("hello!")
    return render_template(
        "employees_adjusted_salaries.html", employees_data=employees_list
    )


@app.route("/salary_less_than_n", methods=["POST"])
def salary_less_than_n():
    salary_threshold = float(request.form["salary_threshold"])
    filtered_employees_data = employee_manager.get_employees_with_salary_less_n(
        salary_threshold
    )
    if filtered_employees_data:
        return render_template("employees.html", employees_data=filtered_employees_data)
    else:
        flash("Nothing was found", "dark")
        return redirect("employees")


@app.route("/retired_employees")
def retired_employees():
    retired_employees_data = employee_manager.get_retirement_employees()
    if retired_employees_data:
        return render_template("employees.html", employees_data=retired_employees_data)
    else:
        flash("Not a single retired employee.", "dark")
        return redirect("employees")


@app.route("/departments", methods=["GET"])
def departments():
    departments_data = sql_dbase.get_all_departments()
    return render_template("departments.html", departments_data=departments_data)


@app.route("/sick_leaves", methods=["POST", "GET"])
def sick_leaves():
    add_sick_leave_form = SickLeaveForm()
    if add_sick_leave_form.validate_on_submit():
        res = sick_leave_manager.add_new_sick_leave(
            new_sick_leave=SickLeave(
                add_sick_leave_form.employee_id.data,
                add_sick_leave_form.start_date.data,
                add_sick_leave_form.end_date.data,
            )
        )
        if not res:
            flash("Failed to add sick leave. Please try again.", "danger")
        else:
            flash("Sick leave added successfully!", "success")
            return redirect(url_for("sick_leaves"))
    return render_template(
        "sick_leaves.html",
        employees_data=employee_manager.get_all_employees(),
        sick_leaves_data=sick_leave_manager.get_all_sick_leaves(),
        pending_sick_leaves_data=sick_leave_manager.get_all_sick_leaves(
            status="Pending"
        ),
        add_sick_leave_form=add_sick_leave_form,
    )


@app.route("/delete_sick_leave/<sick_leave_id>", methods=["POST"])
def delete_sick_leave(sick_leave_id):
    previous_url = request.referrer
    res = sick_leave_manager.delete_sick_leave(sick_leave_id)
    if not res:
        flash("Failed to delete sick leave. Please try again.", "error")
    else:
        flash("Sick leave deleted successfully!", "success")
    return redirect(previous_url or url_for("employees"))


@app.route("/approve_sick_leave/<sick_leave_id>", methods=["POST"])
def approve_sick_leave(sick_leave_id):
    previous_url = request.referrer
    res = sick_leave_manager.approve_sick_leave(sick_leave_id)
    if not res:
        flash("Failed to approve sick leave. Please try again.", "error")
    else:
        flash("Sick leave approved successfully!", "success")
    return redirect(previous_url or url_for("sick_leaves"))


@app.route("/add_sick_leave", methods=["GET, POST"])
def add_sick_leave():
    add_sick_leave_form = SickLeaveForm()
    if add_sick_leave_form.validate_on_submit():
        res = sick_leave_manager.add_new_sick_leave(
            new_sick_leave=SickLeave(
                add_sick_leave_form.employee_id.data,
                add_sick_leave_form.start_date.data,
                add_sick_leave_form.end_date.data,
            )
        )
        if not res:
            flash("Failed to add sick leave. Please try again.", "danger")
        else:
            flash("Sick leave added successfully!", "success")
    return render_template(
        "add_sick_leave.html", add_sick_leave_form=add_sick_leave_form
    )


if __name__ == "__main__":
    app.run(debug=True)
