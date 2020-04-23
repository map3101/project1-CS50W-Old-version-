from flask_login import LoginManager, UserMixin, login_required, logout_user, current_user

class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password