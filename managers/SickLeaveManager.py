from .DBManager import DBManager
from models import SickLeave
from datetime import datetime, timedelta


class SickLeaveManager(DBManager):
    def __init__(self, db):
        super().__init__(db)

    def _get_sick_leaves_list(self, sick_leaves_data):
        return [SickLeave(**sick_leave) for sick_leave in sick_leaves_data]

    def get_all_sick_leaves(self, status="Approved"):
        query_to_exec = (
            "SELECT * FROM Sick_Leaves WHERE status = %s ORDER BY sick_leave_id DESC"
        )
        all_sick_leaves_data = self.execute_query(query=query_to_exec, params=(status,))
        return self._get_sick_leaves_list(all_sick_leaves_data)

    def get_all_sick_leaves_by_employee(self, employee_id, status="Approved"):
        query_to_exec = "SELECT * FROM Sick_Leaves WHERE status = %s AND employee_id = %s ORDER BY end_date DESC"
        all_sick_leaves_data = self.execute_query(
            query=query_to_exec, params=(status, employee_id)
        )
        return self._get_sick_leaves_list(all_sick_leaves_data)

    def get_sick_leaves_by_department(self, department_id, status="Approved"):
        query_to_exec = (
            "SELECT sl.* FROM Sick_Leaves sl "
            "JOIN Employees e ON sl.employee_id = e.employee_id "
            "WHERE e.department_id = %s AND sl.status = %s ORDER BY sl.sick_leave_id DESC"
        )
        sick_leaves_data = self.execute_query(
            query=query_to_exec, params=(department_id, status)
        )
        return self._get_sick_leaves_list(sick_leaves_data)

    def get_sick_leave_by_id(self, sick_leave_id):
        query_to_exec = "SELECT * FROM Sick_Leaves WHERE sick_leave_id = %s;"
        sick_leave_data = self.execute_query(
            query=query_to_exec, params=(sick_leave_id,)
        )
        return self._get_sick_leaves_list(sick_leave_data)

    def get_all_sick_leaves_in_current_month(self, status="Approved"):
        query_to_exec = """SELECT * FROM Sick_Leaves WHERE status = %s 
                            AND (start_date BETWEEN DATE_TRUNC('month', NOW()) AND (DATE_TRUNC('month', NOW()) + INTERVAL '1 month - 1 day')
                            OR end_date BETWEEN DATE_TRUNC('month', NOW()) AND (DATE_TRUNC('month', NOW()) + INTERVAL '1 month - 1 day'));"""
        all_sick_leaves_data_in_current_month_data = self.execute_query(
            query=query_to_exec, params=(status,)
        )
        print(all_sick_leaves_data_in_current_month_data)
        return self._get_sick_leaves_list(all_sick_leaves_data_in_current_month_data)

    def get_all_sick_leaves_in_current_month_by_employee(
        self, employee_id, status="Approved"
    ):
        query_to_exec = """SELECT * FROM Sick_Leaves WHERE status = %s AND employee_id = %s
                            AND (start_date BETWEEN DATE_TRUNC('month', NOW()) AND (DATE_TRUNC('month', NOW()) + INTERVAL '1 month - 1 day')
                            OR end_date BETWEEN DATE_TRUNC('month', NOW()) AND (DATE_TRUNC('month', NOW()) + INTERVAL '1 month - 1 day'));"""
        all_sick_leaves_data_in_current_month_data = self.execute_query(
            query=query_to_exec, params=(status, employee_id)
        )
        print(all_sick_leaves_data_in_current_month_data)
        return self._get_sick_leaves_list(all_sick_leaves_data_in_current_month_data)

    def get_total_pending_sick_leaves(self):
        query_to_exec = "SELECT COUNT(*) FROM Sick_Leaves WHERE status = 'Pending'"
        result = self.execute_query(query=query_to_exec)
        return result[0][0] if result else 0

    def add_new_sick_leave(self, new_sick_leave):
        query_to_exec = """
            INSERT INTO sick_leaves (employee_id, start_date, end_date, status)
            VALUES (%s, %s, %s, %s)
            RETURNING sick_leave_id;
            """
        new_sick_leave_data = (
            new_sick_leave.employee_id,
            new_sick_leave.start_date,
            new_sick_leave.end_date,
            new_sick_leave.status,
        )
        new_sick_leave_id = self.execute_query(
            query=query_to_exec, params=new_sick_leave_data
        )
        self._db.commit()
        return new_sick_leave_id[0].get("sick_leave_id") if new_sick_leave_id else None

    def delete_sick_leave(self, sick_leave_id_to_delete):
        query_to_exec = "DELETE FROM sick_leaves WHERE sick_leave_id = %s RETURNING *"
        deleted_sick_leave = self.execute_query(
            query=query_to_exec, params=(sick_leave_id_to_delete,)
        )
        self._db.commit()
        return bool(deleted_sick_leave)

    def approve_sick_leave(self, sick_leave_id):
        existing_sick_leave = self.get_sick_leave_by_id(sick_leave_id)

        if not existing_sick_leave:
            return False

        if existing_sick_leave[0].status != "Approved":
            query_to_exec = (
                "UPDATE Sick_Leaves SET status = 'Approved' WHERE sick_leave_id = %s;"
            )
            self.execute_query(query=query_to_exec, params=(sick_leave_id,))
            self._db.commit()
            return True

        return False
