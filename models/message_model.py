from .shared import db


class MessageModel(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    sender = db.relationship("UserModel")
    time = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String(1000), nullable=False)
    is_read = db.Column(db.Boolean)


    def __init__(self, sender, time, message):
        self.sender = sender
        self.time = time
        self.message = message
        self.is_read = False

    def __repr__(self):
        return f"From: {self.sender_id}, message: {self.message}, at: {self.time}"
