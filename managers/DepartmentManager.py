from .DBManager import DBManager
from models import Department
from datetime import datetime, timedelta


class DepartmentManager(DBManager):
    def __init__(self, db):
        super().__init__(db)
