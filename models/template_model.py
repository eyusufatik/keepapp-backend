from typing_extensions import Self
from .shared import db


class TemplateModel(db.Model):
    __tablename__ = "templates"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="---")
    empty_template = db.Column(db.JSON, nullable=False)
    rooms_using = db.relationship("RoomModel", backref="template", lazy=True)

    def __init__(self, name, empty_template):
        self.name = name
        self.empty_template = empty_template
