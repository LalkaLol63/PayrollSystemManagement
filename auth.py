import redis
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, url_for
from functools import wraps


class Authentication:
    def __init__(self):
        self.__r = self.connect_to_redis_db()

    def connect_to_redis_db(self):
        redis_cli = redis.Redis(
            host="localhost", port=6379, db=0, password="secretpass"
        )
        return redis_cli

    def authenticate(self, user_id, user_password):
        user_data = self.get_user_data(user_id)

        if user_data and check_password_hash(user_data["password"], user_password):
            if user_data["role"] == "admin":
                session["admin_logged"] = 1
            else:
                session["employee_logged"] = 1
            session["user_id"] = user_id
            return True  # Authentication successful
        else:
            return False  # Authentication failed

    def get_user_role(self, user_id):
        user_data = self.get_user_data()
        if user_data:
            return user_data.get("role")
        return None

    def get_current_user_id(self):
        if "user_id" in session and session["user_id"] is not None:
            return session["user_id"]
        else:
            return None

    def get_user_data(self, user_id):
        key = f"user:{user_id}"
        data_bytes = self.__r.hgetall(key)
        data = {
            key.decode("utf-8"): value.decode("utf-8")
            for key, value in data_bytes.items()
        }
        return data

    def admin_login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "admin_logged" not in session or session["admin_logged"] is None:
                print("not logged admin")
                return redirect("login")
            print("logged admin")
            print(session)
            return f(*args, **kwargs)

        return decorated_function

    def employee_login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "admin_logged" not in session:
                if (
                    "employee_logged" not in session
                    or session["user_id"] != kwargs["employee_id"]
                ):
                    return redirect(url_for("home"))
            return f(*args, **kwargs)

        return decorated_function

    def add_user(self, user_id, user_password, user_role="employee"):
        if self.get_user_data(user_id):
            return False
        else:
            key = f"user:{user_id}"
            self.__r.hset(key, "password", generate_password_hash(user_password))
            self.__r.hset(key, "role", user_role)
            return True

    def delete_user(self, user_id):
        key = f"user:{user_id}"
        if not self.__r.exists(key):
            return False
        self.__r.delete(key)
        return True
