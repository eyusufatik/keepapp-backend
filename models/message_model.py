from .shared import db


class MessageModel(db.Model):
    """
    One way messages from keepers to admins.
    """
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    time = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String(1000), nullable=False)
    is_read = db.Column(db.Boolean)


    def __init__(self, time, message):
        self.time = time
        self.message = message
        self.is_read = False

    def __repr__(self):
        return f"From: {self.sender_id}, message: {self.message}, at: {self.time}"
