from .DBManager import DBManager
from models import Department
from datetime import datetime, timedelta


class DepartmentManager(DBManager):
    def __init__(self, db):
        super().__init__(db)

    def _get_departments_list(self, departments_data):
        return [Department(**department) for department in departments_data]

    def get_all_departments(self):
        query_to_exec = """SELECT
                            d.department_id,
                            d.department_name,
                            COUNT(e.employee_id) AS num_employees,
                            AVG(CASE WHEN e.gender = 'Male' THEN e.monthly_salary END) AS avg_salary_male,
                            AVG(CASE WHEN e.gender = 'Female' THEN e.monthly_salary END) AS avg_salary_female,
                            AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_of_birth))) AS avg_employee_age,
                            AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_of_employment))) AS avg_work_experience
                            FROM
                                Departments d
                            LEFT JOIN
                                Employees e ON d.department_id = e.department_id
                            GROUP BY
                                d.department_id;"""
        all_departments_data = self.execute_query(query=query_to_exec)
        print(all_departments_data)
        return self._get_departments_list(all_departments_data)

    def get_department_by_id(self, department_id):
        query_to_exec = """SELECT
                            d.department_id,
                            d.department_name,
                            COUNT(e.employee_id) AS num_employees,
                            AVG(CASE WHEN e.gender = 'Male' THEN e.monthly_salary END) AS avg_salary_male,
                            AVG(CASE WHEN e.gender = 'Female' THEN e.monthly_salary END) AS avg_salary_female,
                            AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_of_birth))) AS avg_employee_age,
                            AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_of_employment))) AS avg_work_experience
                            FROM
                                Departments d
                            LEFT JOIN
                                Employees e ON d.department_id = e.department_id
                            WHERE 
                                d.department_id = %s
                            GROUP BY
                                d.department_id;"""
        department_data = self.execute_query(
            query=query_to_exec, params=(department_id,)
        )
        return self._get_departments_list(department_data)
