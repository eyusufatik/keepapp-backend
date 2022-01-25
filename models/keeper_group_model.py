from .shared import db

keeper_group_pairings = db.Table("keeper_group_pairings",
                                 db.Column("keeper_id", db.ForeignKey(
                                     "users.id"), primary_key=True),
                                 db.Column("keeper_groups.id", db.ForeignKey(
                                     "keeper_groups.id"), primary_key=True)
                                 )


class KeeperGroupModel(db.Model):
    __tablename__ = "keeper_groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    keepers = db.relationship("UserModel", secondary=keeper_group_pairings,
                              lazy="subquery", backref=db.backref("keeper_groups", lazy=True))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Group name: {self.name}"
