from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal


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
        current_month_sick_leaves_duration=0,
        adjusted_salary=None,
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
        self.current_month_sick_leaves_duration = current_month_sick_leaves_duration
        self.adjusted_salary = adjusted_salary

    def calculate_work_experience(self):
        current_date = datetime.now().date()
        work_experience = (current_date - self.date_of_employment).days // 365
        return work_experience

    def calculate_current_month_sick_leaves_duration(self, curr_month_sick_leaves):
        duration_sum = 0
        for sick_leave in curr_month_sick_leaves:
            start_date_in_month = max(
                sick_leave.start_date, datetime.today().date() + relativedelta(day=1)
            )
            end_date_in_month = min(
                sick_leave.end_date, datetime.today().date() + relativedelta(day=31)
            )
            sick_leave_duration_in_month = (
                end_date_in_month - start_date_in_month
            ).days + 1
            duration_sum += sick_leave_duration_in_month
        print(duration_sum)
        self.current_month_sick_leaves_duration = duration_sum

    def calculate_adjusted_salary(self):
        if self.work_experience < 2:
            sick_leave_percentage = 0.5
        elif 2 <= self.work_experience < 4:
            sick_leave_percentage = 0.2
        else:
            sick_leave_percentage = 0.0
        print("duration:", self.current_month_sick_leaves_duration)
        adjusted_salary = float(self.monthly_salary) * (
            1 - sick_leave_percentage * self.current_month_sick_leaves_duration / 30
        )
        self.adjusted_salary = adjusted_salary


class Department:
    def __init__(
        self,
        department_id,
        department_name,
        num_employees=0,
        avg_salary_male=0,
        avg_salary_female=0,
        avg_work_experience=0,
        avg_employee_age=0,
        total_sick_leave_duration=0,
    ):
        self.department_id = department_id
        self.department_name = department_name
        self.num_employees = num_employees
        self.avg_salary_male = avg_salary_male
        self.avg_salary_female = avg_salary_female
        self.avg_work_experience = avg_work_experience
        self.avg_employee_age = avg_employee_age
        self.total_sick_leave_duration = total_sick_leave_duration

    def calculate_sick_leave_durations(self, sick_leave_list):
        self.sick_leave_durations = {}

        for sick_leave in sick_leave_list:
            current_date = sick_leave.start_date
            end_date = sick_leave.end_date
            while current_date <= end_date:
                year_month = current_date.strftime("%Y-%m")
                if year_month not in self.sick_leave_durations:
                    self.sick_leave_durations[year_month] = 1
                else:
                    self.sick_leave_durations[year_month] += 1
                current_date += timedelta(days=1)

        self.total_sick_leave_duration = sum(self.sick_leave_durations.values())


class SickLeave:
    def __init__(
        self, employee_id, start_date, end_date, status="Approved", sick_leave_id=None
    ):
        self.sick_leave_id = sick_leave_id
        self.employee_id = employee_id
        self.start_date = start_date
        self.end_date = end_date
        self.duration = self.calculate_duration()
        self.status = status

    def calculate_duration(self):
        duration = (self.end_date - self.start_date).days + 1
        return duration
