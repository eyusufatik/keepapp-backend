from .shared import db


class RecordModel(db.Model):
    __tablename__ = "records"
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    keeper_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filled_list = db.Column(db.JSON, nullable=False)
    note = db.Column(db.String(2000))
    photos = db.Column(db.ARRAY(db.String()))

    def __init__(self, time, filled_list, note, photos):
        self.time = time
        self.filled_list = filled_list
        self.note = note,
        self.photos = photos