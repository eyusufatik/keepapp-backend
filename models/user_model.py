import enum
from .shared import db


class UserType(enum.IntEnum):
    super_admin = 0
    admin = 1
    keeper = 2


class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.Enum(UserType), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, user_type, username, password):
        self.user_type = user_type
        self.username = username
        self.password = password

    def __repr__(self):
        return f"User: id = {self.id}, name = {self.username}, type = {self.user_type}"
