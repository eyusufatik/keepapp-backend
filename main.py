# import from libs
from datetime import datetime, timedelta
from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, current_user, jwt_required, set_access_cookies, unset_jwt_cookies
import bcrypt

# import from own code
from app_configs import *
from models.user_model import UserModel, UserType
from models.message_model import MessageModel
from models.keeper_group_model import KeeperGroupModel
from models.room_model import RoomModel, RoomStatus
from models.template_model import TemplateModel
from models.record_model import RecordModel
from models.shared import db
from parsers import *
from util_funcs import *
from decorators import *


@app.route("/user/register", methods=["POST"])
def register():
    args = user_registration_parser.parse_args()
    user_type = UserType(args["userType"])
    username = args["username"]
    password = args["password"]
    if len(password) < 8:
        return success_patcher({"msg": "Password must be at least 8 characters."}, 0), 400

    if UserModel.query.filter_by(username=username).count() > 0:
        return success_patcher({"msg": "User already exists"}, 0), 409
    else:
        hashed_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user = UserModel(user_type,
                         username, hashed_pass.decode())
        db.session.add(user)
        db.session.commit()
        return success_patcher({}, 1), 201


@app.route("/user/login", methods=["POST"])
def login():
    args = user_login_parser.parse_args(req=request)
    username = args["username"]
    password = args["password"]
    user_from_db = UserModel.query.filter_by(username=username).scalar()
    if user_from_db != None:
        if bcrypt.checkpw(password.encode(), user_from_db.password.encode()):
            response = success_patcher({"msg": "Logged in successfully"}, 1)
            access_token = create_access_token(identity=user_from_db)
            response = jsonify(response)
            set_access_cookies(response, access_token)
            return response, 200
        else:
            return jsonify(success_patcher({"msg": "Invalid username or password"}, 0)), 400
    else:
        return jsonify(success_patcher({"msg": "Invalid username or password"}, 0)), 400


@app.route("/user/logout", methods=["GET"])
def logout_with_cookies():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


class Rooms(Resource):
    @jwt_required()
    def get(self, id=None):
        # /rooms
        if id is None:
            user_rooms = {}
            if current_user.user_type == UserType.admin or current_user.user_type == UserType.super_admin:
                all_rooms = RoomModel.query.all()
                user_rooms = room_model_list_to_dict(all_rooms)
            else:
                room_set = set()
                for group in current_user.keeper_groups:
                    for room in group.rooms:
                        room_set.add(room)
                user_rooms = room_model_list_to_dict(room_set)
            return success_patcher(user_rooms, 1), 200
        # /rooms/<id>
        else:
            room = RoomModel.query.filter_by(id=id).scalar()

            if room is None:
                return success_patcher({"msg": "Room with given ID doesn't exist."}, 0), 400

            if current_user.user_type == UserType.keeper and not check_room_access(current_user, room):
                return success_patcher({"msg": "Keeper doesn't have access to the room, add it to a group that has access to the room"}, 0), 400

            room_dict = room_model_to_dict(room)
            return success_patcher(room_dict, 1), 200

    @jwt_required()
    @only_admin
    def post(self):
        args = create_room_parser.parse_args()
        name = args["name"]
        keeper_group_id = args["keeperGroupId"]
        check_list = args["checkList"]
        template_id = args["templateId"]

        if not RoomModel.query.filter_by(name=name).scalar() is None:
            return success_patcher({"msg": "There is already a room with this name."}, 0), 400

        if check_list is None and template_id is None:
            return success_patcher({"msg": "checkList and templateId cannot be both empty"}, 0), 400

        if not check_list is None and not template_id is None:
            return success_patcher({"msg": "Only one of checkList or templateId should be given."}, 0), 400

        new_room = RoomModel(name)

        if not keeper_group_id is None:
            group = KeeperGroupModel.query.filter_by(
                id=keeper_group_id).scalar()
            if group is None:
                return success_patcher({"msg": "No such keeper group exists."}, 0), 400
            else:
                new_room.keeper_groups.append(group)

        if not check_list is None:
            new_template = TemplateModel(name, {"checkList": check_list})
            new_template.single_use = True
            new_template.rooms_using.append(new_room)
            db.session.add(new_template)
        elif not template_id is None:
            template = TemplateModel.query.filter_by(id=template_id).scalar()
            if template is None:
                return success_patcher({"msg": "No such template exists."}, 0), 400
            else:
                template.rooms_using.append(new_room)

        db.session.commit()
        return success_patcher({"id": new_room.id}, 1), 200


class RoomRecords(Resource):
    @jwt_required()
    def get(self, id):
        args = date_in_query_parser.parse_args()
        date = args["date"]
        room = RoomModel.query.filter_by(id=id).scalar()

        if room is None:
            return success_patcher({"msg": "Room with given ID doesn't exist."}, 0), 400

        if check_room_access(current_user, room):
            record = None

            if date is None:
                record = RecordModel.query.filter_by(room_id=id).filter(
                    RecordModel.time <= datetime.now()).filter(datetime.today().date() <= RecordModel.time).scalar()
            else:
                print(date)
                record = RecordModel.query.filter_by(room_id=id).filter(
                    RecordModel.time >= date).filter(RecordModel.time <= date+timedelta(days=1)).scalar()

            if record is None:
                return success_patcher({"msg": "No record for the room today/at the given date."}, 0), 400
            return_dict = {}
            return_dict["checkList"] = record.filled_list
            return_dict["notes"] = record.notes
            return_dict["photos"] = record.photos
            return_dict = {"record": return_dict}

            return success_patcher(return_dict, 1), 200

        else:
            return success_patcher({"msg": "User doesn't have access to the room"}, 0), 400

    def post(self, id):
        pass


api.add_resource(Rooms, "/rooms",  "/rooms/<int:id>")
api.add_resource(RoomRecords, "/rooms/<int:id>/records")

if __name__ == "__main__":
    app.run(debug=True)
