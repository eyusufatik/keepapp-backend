from .shared import db

# table for keeper-keeper group many to many relationship.
keeper_group_pairings = db.Table("keeper_group_pairings",
                                 db.Column("keeper_id", db.ForeignKey(
                                     "users.id"), primary_key=True),
                                 db.Column("keeper_groups.id", db.ForeignKey(
                                     "keeper_groups.id"), primary_key=True)
                                 )


class KeeperGroupModel(db.Model):
    """
    Keeper groups are assigned rooms and keepers. Assigned keeper accounts will be able to POST and GET records for the room.
    """
    __tablename__ = "keeper_groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    keepers = db.relationship("UserModel", secondary=keeper_group_pairings,
                              lazy="subquery", backref=db.backref("keeper_groups", lazy=True))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Group name: {self.name}"
