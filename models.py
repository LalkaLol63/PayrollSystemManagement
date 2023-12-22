from datetime import datetime


class Employee:
    def __init__(
        self,
        department_id,
        name,
        monthly_salary,
        date_of_birth,
        date_of_employment,
        marital_status,
        gender,
        number_of_children,
        employee_id=None,
    ):
        self.employee_id = employee_id
        self.department_id = department_id
        self.name = name
        self.monthly_salary = monthly_salary
        self.date_of_birth = date_of_birth
        self.date_of_employment = date_of_employment
        self.marital_status = marital_status
        self.gender = gender
        self.number_of_children = number_of_children
        self.work_experience = self.calculate_work_experience()

    def calculate_work_experience(self):
        current_date = datetime.now().date()
        work_experience = (current_date - self.date_of_employment).days // 365
        return work_experience


class Department:
    def __init__(self, department_id, department_name):
        self.department_id = department_id
        self.department_name = department_name


class SickLeave:
    def __init__(self, sick_leave_id, employee_id, start_date, end_date):
        self.sick_leave_id = sick_leave_id
        self.employee_id = employee_id
        self.start_date = start_date
        self.end_date = end_date
        self.duration = self.calculate_duration()

    def calculate_duration(self):
        start_datetime = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(self.end_date, "%Y-%m-%d")
        duration = (end_datetime - start_datetime).days + 1
        return duration
