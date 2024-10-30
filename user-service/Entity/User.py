class User:
    def __init__(self, username, email, password, jwt_token):
        self.username = username
        self.email = email
        self.password = password
        self.jwt_token = jwt_token
