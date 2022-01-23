import enum
from .shared import db


class UserType(enum.Enum):
    super_admin = 0
    admin = 1
    keeper = 2


class UserModel(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50))
    user_type = db.Column(db.Enum(UserType))
    username = db.Column(db.String(100))
    password = db.Column(db.String(120))

    def __init__(self, company_name, user_type, username, password):
        self.company_name = company_name
        self.user_type = user_type
        self.username = username
        self.password = password

    def __repr__(self):
        return f"User: company = {self.company_name}, name = {self.username}, type = {self.user_type}"
