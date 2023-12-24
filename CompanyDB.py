from flask import g
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timedelta


class CompanyDB:
    def __init__(self, db):
        self.__db = db
        self.__cursor = db.cursor(cursor_factory=DictCursor)

    def get_all_employees(self):
        try:
            self.__cursor.execute("SELECT * FROM Employees3 ORDER BY name DESC;")
            all_employees_data = self.__cursor.fetchall()
            if all_employees_data:
                return all_employees_data
        except psycopg2.Error as e:
            print("Помилка отримання даних з бд" + str(e))
        return []

    def get_employee_by_id(self, employee_id):
        try:
            self.__cursor.execute(
                "SELECT * FROM Employees3 WHERE employee_id = %s;", (employee_id,)
            )
            employee_data = self.__cursor.fetchall()
            print(employee_data)
            if employee_data:
                return employee_data
        except psycopg2.Error as e:
            print("Помилка отримання даних з бд" + str(e))
        return []

    def get_employee_by_name(self, employee_name):
        try:
            self.__cursor.execute(
                "SELECT * FROM Employees3 WHERE name = %s;", (employee_name,)
            )
            employees_data = self.__cursor.fetchall()
            print(employees_data)
            if employees_data:
                return employees_data
        except psycopg2.Error as e:
            print("Помилка отримання даних з бд" + str(e))
        return []

    def get_employees_with_salary_less_n(self, max_salary):
        try:
            self.__cursor.execute(
                "SELECT * FROM Employees3 WHERE monthly_salary < %s;", (max_salary,)
            )
            employees_data = self.__cursor.fetchall()
            print(employees_data)
            if employees_data:
                return employees_data
        except psycopg2.Error as e:
            print("Помилка отримання даних з бд" + str(e))
        return []

    def get_retirement_employees(self):
        try:
            date_63_years_ago = datetime.now() - timedelta(days=63 * 365)
            self.__cursor.execute(
                "SELECT * FROM Employees3 WHERE date_of_birth < %s;",
                (date_63_years_ago,),
            )
            employees_data = self.__cursor.fetchall()
            print(employees_data)
            if employees_data:
                return employees_data
        except psycopg2.Error as e:
            print("Помилка отримання даних з бд" + str(e))
        return []

    def add_new_employee(self, new_employee_info):
        try:
            self.__cursor.execute(
                """
            INSERT INTO Employees3 (department_id, name, monthly_salary, date_of_birth, date_of_employment, marital_status, gender, number_of_children)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING employee_id;
            """,
                (
                    int(new_employee_info["department_id"]),
                    new_employee_info["name"],
                    float(new_employee_info["monthly_salary"]),
                    new_employee_info["date_of_birth"],
                    new_employee_info["date_of_employment"],
                    new_employee_info["marital_status"],
                    new_employee_info["gender"],
                    int(new_employee_info["number_of_children"]),
                ),
            )
            employee_id = self.__cursor.fetchone().get("employee_id")
            self.__db.commit()
            print(employee_id)
            return employee_id
        except psycopg2.Error as e:
            print("Помилка додавання даних до бд" + str(e))
            return None

    def delete_employee(self, employee_id_to_delete):
        try:
            self.__cursor.execute(
                "DELETE FROM Employees3 WHERE employee_id = %s",
                (employee_id_to_delete,),
            )
            self.__db.commit()
        except psycopg2.Error as e:
            print("Помилка видалення даних з бд" + str(e))
            return False
        return True

    def get_all_departments(self):
        try:
            current_year = datetime.now().year
            self.__cursor.execute(
                (
                    """SELECT
                            d.department_id,
                            d.department_name,
                            COUNT(e.employee_id) AS num_employees,
                            AVG(CASE WHEN e.gender = 'Male' THEN e.monthly_salary END) AS avg_salary_male,
                            AVG(CASE WHEN e.gender = 'Female' THEN e.monthly_salary END) AS avg_salary_female,
                            AVG(%s - EXTRACT(YEAR FROM e.date_of_employment)) AS avg_work_experience,
                        FROM
                            Departments3 d
                        JOIN
                            Employees3 e ON d.department_id = e.department_id
                        GROUP BY
                            d.department_id;"""
                ),
                (current_year,),
            )
            all_departments_data = self.__cursor.fetchall()
            print(all_departments_data)
            if all_departments_data:
                return all_departments_data
        except psycopg2.Error as e:
            print("Помилка отримання даних з бд" + str(e))
        return []

    def get_sick_leaves(self):
        try:
            self.__cursor.execute("SELECT * FROM sick_leaves3;")
            sick_leaves_data = self.__cursor.fetchall()
            print(sick_leaves_data)
            if sick_leaves_data:
                return sick_leaves_data
        except psycopg2.Error as e:
            print("Помилка отримання даних з бд" + str(e))
        return []

    def add_new_sick_leave(self, new_sick_leave_info):
        try:
            self.__cursor.execute(
                """
                           INSERT INTO sick_leaves3(employee_id, start_date, end_date)
                           VALUES (%s, %s, %s)
                       """,
                (
                    int(new_sick_leave_info["employee_id"]),
                    new_sick_leave_info["start_date"],
                    new_sick_leave_info["end_date"],
                ),
            )
            self.__db.commit()
        except psycopg2.Error as e:
            print("Помилка додавання даних до бд" + str(e))
            return False
        return True
