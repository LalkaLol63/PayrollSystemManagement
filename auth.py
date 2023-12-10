
def authenticate(username, password):

    stored_username = "admin"
    stored_password = "a"

    if username == stored_username and password == stored_password:
        return True  # Authentication successful
    else:
        return False  # Authentication failed
