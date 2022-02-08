import enum
from .shared import db
from .record_model import RecordModel

group_room_pairings = db.Table("group_room_pairings",
                               db.Column("group_id", db.ForeignKey(
                                   "keeper_groups.id"), primary_key=True),
                               db.Column("room_id", db.ForeignKey(
                                   "rooms.id"), primary_key=True)
                               )


class RoomStatus(enum.IntEnum):
    closed = 0
    not_checked = 1
    missing_items = 2
    damaged_items = 3
    okay = 4
    missing_and_damaged = 23
    # not burası main


class RoomModel(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    status = db.Column(db.Enum(RoomStatus))
    keeper_groups = db.relationship("KeeperGroupModel", secondary=group_room_pairings,
                             lazy="subquery", backref=db.backref("rooms", lazy=True))
    template_id = db.Column(db.Integer, db.ForeignKey("templates.id"), nullable=True)
    records = db.relationship("RecordModel", backref="room", lazy=True)

    def __init__(self, name):
        self.name = name
        self.status = RoomStatus.not_checked

    def __repr__(self):
        return f"Name: {self.name}, status: {self.status.name}"