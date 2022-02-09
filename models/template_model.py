from email.policy import default
from typing_extensions import Self
from .shared import db


class TemplateModel(db.Model):
    __tablename__ = "templates"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="---")
    empty_template = db.Column(db.JSON, nullable=False)
    rooms_using = db.relationship("RoomModel", backref="template", lazy=True)
    single_use = db.Column(db.Boolean, default=False)

    def __init__(self, name, empty_template):
        self.name = name
        self.empty_template = empty_template

    def __repr__(self):
        return f"Id: {self.id}, name: {self.name}"