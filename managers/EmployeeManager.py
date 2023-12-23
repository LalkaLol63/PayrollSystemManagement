from .DBManager import DBManager
from models import Employee
from datetime import datetime, timedelta


class EmployeeManager(DBManager):
    RETIREMENT_AGE = 63

    def __init__(self, db):
        super().__init__(db)

    def _get_employee_list(self, employees_data):
        return [Employee(**employee_data) for employee_data in employees_data]

    def get_all_employees(self):
        query_to_exec = "SELECT * FROM Employees ORDER BY name DESC;"
        all_employees_data = self.execute_query(query=query_to_exec)
        return self._get_employee_list(all_employees_data)

    def get_employee_by_id(self, employee_id):
        query_to_exec = "SELECT * FROM Employees WHERE employee_id = %s;"
        employee_data = self.execute_query(query=query_to_exec, params=(employee_id,))
        return self._get_employee_list(employee_data)[0]

    def get_employee_by_name(self, employee_name):
        query_to_exec = "SELECT * FROM Employees WHERE name = %s;"
        employees_data = self.execute_query(
            query=query_to_exec, params=(employee_name,)
        )
        return self._get_employee_list(employees_data)

    def get_employees_with_salary_less_n(self, max_salary):
        query_to_exec = "SELECT * FROM Employees WHERE monthly_salary < %s;"
        employees_data = self.execute_query(query=query_to_exec, params=(max_salary,))
        return self._get_employee_list(employees_data)

    def get_retirement_employees(self):
        min_date_of_birth_of_retirement = datetime.now() - timedelta(
            days=EmployeeManager.RETIREMENT_AGE * 365
        )
        query_to_exec = "SELECT * FROM Employees WHERE monthly_salary < %s;"
        retired_employees_data = self.execute_query(
            query=query_to_exec, params=(min_date_of_birth_of_retirement,)
        )
        return self._get_employee_list(retired_employees_data)

    def add_new_employee(self, new_employee):
        query_to_exec = """
            INSERT INTO Employees (department_id, name, monthly_salary, date_of_birth, date_of_employment, marital_status, gender, number_of_children)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING employee_id;
            """
        new_employee_data = (
            new_employee.department_id,
            new_employee.name,
            new_employee.monthly_salary,
            new_employee.date_of_birth,
            new_employee.date_of_employment,
            new_employee.marital_status,
            new_employee.gender,
            new_employee.number_of_children,
        )
        new_employee_id = self.execute_query(
            query=query_to_exec, params=new_employee_data
        )
        self._db.commit()
        return new_employee_id[0].get("employee_id") if new_employee_id else None

    def delete_employee(self, employee_id_to_delete):
        query = "DELETE FROM Employees WHERE employee_id = %s RETURNING *"
        deleted_employee = self.execute_query(query, (employee_id_to_delete,))
        self._db.commit()
        return bool(deleted_employee)
