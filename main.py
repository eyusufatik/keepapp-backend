# import from libs
from datetime import datetime, timedelta
from email.message import Message
from pyexpat.errors import messages
from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, current_user, jwt_required, set_access_cookies, unset_jwt_cookies
import bcrypt
from sqlalchemy import true

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


@app.route("/users/register", methods=["POST"])
def register():
    args = user_registration_parser.parse_args()
    user_type = UserType(args["userType"])
    username = args["username"]
    password = args["password"]

    # TODO: Discuss better password enforcement.
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
        return success_patcher({"msg": "User registered successfully."}, 1), 201


@app.route("/users/login", methods=["POST"])
def login():
    args = user_login_parser.parse_args(req=request)
    username = args["username"]
    password = args["password"]

    user_from_db = UserModel.query.filter_by(username=username).scalar()

    if user_from_db != None and bcrypt.checkpw(password.encode(), user_from_db.password.encode()):
        response = success_patcher(
            {"msg": "Logged in successfully"}, 1)
        access_token = create_access_token(identity=user_from_db)
        response = jsonify(response)
        set_access_cookies(response, access_token)
        return response, 200
    else:
        return jsonify(success_patcher({"msg": "Invalid username or password"}, 0)), 400


@app.route("/users/logout", methods=["GET"])
def logout_with_cookies():
    response = jsonify({"msg": "logout successful", "success": 1})
    unset_jwt_cookies(response)
    return response


class Users(Resource):
    @jwt_required()
    @only_admin
    def get(self, id=None):
        # /users
        if id is None:
            users = UserModel.query.filter(
                UserModel.user_type != UserType.super_admin).all()

            if users is None:
                return success_patcher({"msg": "No users currently."}, 0), 400

            return_dict = user_model_list_to_dict(users)
            return success_patcher(return_dict, 1), 200
        # /users/{id}
        else:
            user = UserModel.query.filter(
                UserModel.user_type != UserType.super_admin).filter_by(id=id).scalar()

            if user is None:
                return success_patcher({"msg": "User with given ID doesn't exist."}, 0), 400

            return_dict = user_model_to_dict(user)

            return success_patcher(return_dict, 1), 200

    @jwt_required()
    @only_admin
    def put(self, id=None):
        args = update_user_parser.parse_args()
        old_password = args["oldPassword"]
        new_password = args["newPassword"]
        keeper_group_ids = args["keeperGroupIds"]

        user = UserModel.query.filter_by(id=id).scalar()

        if id is None and current_user.user_type == UserType.admin:
            user = current_user

        if user is None:
            return success_patcher({"msg": "User with given ID doesn't exist."}, 0), 400

        if (not old_password is None or not new_password is None) and not keeper_group_ids is None:
            return success_patcher({"msg": "Either update the password or the keeper groups at the same time."}, 0), 400

        if user.user_type == UserType.keeper and not new_password is None:
            if len(new_password) < 8:
                return success_patcher({"msg": "Password must be at least 8 characters."}, 0), 400
            hashed_pass = bcrypt.hashpw(
                new_password.encode(), bcrypt.gensalt())
            user.password = hashed_pass.decode()
            db.session.commit()
            return success_patcher({"msg": "Password successfully updated."}, 1), 200
        elif user.user_type == UserType.admin and not new_password is None and not old_password is None:
            if bcrypt.checkpw(old_password.encode(), user.password.encode()):
                if len(new_password) < 8:
                    return success_patcher({"msg": "Password must be at least 8 characters."}, 0), 400
                hashed_pass = bcrypt.hashpw(
                    new_password.encode(), bcrypt.gensalt())
                user.password = hashed_pass.decode()
                db.session.commit()
            return success_patcher({"msg": "Password successfully updated."}, 1), 200
        elif not keeper_group_ids is None:
            if user.user_type == UserType.keeper:
                user.keeper_groups.clear()
                db.session.commit()
                for id in keeper_group_ids:
                    group = KeeperGroupModel.query.filter_by(id=id).scalar()

                    if group is None:
                        return success_patcher({"msg": f"Group with id {id} doesn't exist."}, 0), 400
                    else:
                        group.keepers.append(user)

                db.session.commit()
                return success_patcher({"msg": "Keeper assigned to given groups successfully."}, 1), 200
            else:
                return success_patcher({"msg": "Only keepers can be assigned to keeper groups."}, 0), 400
        else:
            return success_patcher({"msg": "Both the newPassword field and the oldPassword field or the keeperGroupIds field must be filled."}, 0), 400

    @jwt_required()
    @only_admin
    def delete(self, id=None):
        user = UserModel.query.filter(
            UserModel.user_type != UserType.super_admin).filter_by(id=id).scalar()

        if user is None:
            return success_patcher({"msg": "User with given ID doesn't exist."}, 0), 400

        if user.user_type != UserType.keeper:
            return success_patcher({"msg": "Admin accounts cannot be deleted."}, 0), 400

        db.session.delete(user)
        db.session.commit()

        return success_patcher({"msg": "Account deleted succesffully."}, 1), 200


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
        names = args["names"]
        check_list = args["checkList"]
        template_id = args["templateId"]

        if check_list is None and template_id is None:
            return success_patcher({"msg": "checkList and templateId cannot be both empty"}, 0), 400

        if not check_list is None and not template_id is None:
            return success_patcher({"msg": "Only one of checkList or templateId should be given."}, 0), 400

        template = TemplateModel.query.filter_by(id=template_id).scalar()
        if not check_list is None:
            new_template = TemplateModel(
                "single use", {"checkList": check_list})
            new_template.single_use = True
            db.session.add(new_template)
        elif not template_id is None:
            if template is None:
                return success_patcher({"msg": "No such template exists."}, 0), 400

        new_room_ids = {}

        for name in names:
            if not RoomModel.query.filter_by(name=name).scalar() is None:
                return success_patcher({"msg": "There already exists a room with the name: "+name}, 0), 400

            new_room = RoomModel(name)

            if not check_list is None:
                new_template.rooms_using.append(new_room)
            elif not template_id is None:
                template.rooms_using.append(new_room)

            db.session.commit()
            new_room_ids[name] = new_room.id
        return success_patcher({"newRooms": new_room_ids}, 1), 200


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

            return_dict = {
                "checkList": record.filled_list,
                "notes": record.notes,
                "photos":  record.photos
            }
            return_dict = {"record": return_dict}

            return success_patcher(return_dict, 1), 200

        else:
            return success_patcher({"msg": "User doesn't have access to the room"}, 0), 400

    @jwt_required()
    @only_keeper
    def post(self, id):
        args = create_record_parser.parse_args()
        check_list = args["checkList"]
        note = args["notes"]
        photos = args["photos"]

        room = RoomModel.query.filter_by(id=id).scalar()

        if room is None:
            return success_patcher({"msg": "Room with given ID doesn't exist."}, 0), 400

        if not check_room_access(current_user, room):
            return success_patcher({"msg": "User doesn't have access to the room"}, 0), 400

        if not check_item_values(check_list):
            return success_patcher({"msg": "Items must only be assigned 2,3 or 4."}, 0), 400

        if is_check_list_for_room(room, check_list):
            record = RecordModel(datetime.now(), check_list, note, photos)
            with db.session.no_autoflush:
                current_user.records.append(record)
                room.records.append(record)
                room.status = get_room_status_from_check_list(check_list)
                db.session.commit()
            return success_patcher({"msg": "Record created successfully."}, 1), 200
        else:
            return success_patcher({"msg": "Sent checkList doesn't fit the room's template."}, 0), 400


class Templates(Resource):
    @jwt_required()
    @only_admin
    def get(self, id=None):
        return_dict = {}
        # /templates
        if id is None:
            all_templates = TemplateModel.query.filter_by(
                single_use=False).all()
            return_dict = template_model_list_to_dict(all_templates)
        # /templates/{id}
        else:
            template = TemplateModel.query.filter_by(id=id).scalar()

            if template is None:
                return success_patcher({"msg": "No such template exists"}, 0), 400

            return_dict = template_model_to_dict(template)

        return success_patcher(return_dict, 1), 200

    @jwt_required()
    @only_admin
    def post(self, id=None):
        if not id is None:
            return success_patcher({"msg": "No id in POST /templates."}, 0), 400

        args = create_template_parser.parse_args()
        name = args["name"]
        check_list = args["checkList"]

        template = TemplateModel(name, {"checkList": check_list})
        db.session.add(template)
        db.session.commit()

        return success_patcher({"id": template.id}, 1), 200

    @jwt_required()
    @only_admin
    def put(self, id=None):
        if id is None:
            return success_patcher({"msg": "Provide the id of the template you want to edit."}, 0), 400

        args = update_template_parser.parse_args()
        name = args["name"]
        check_list = args["checkList"]

        template = TemplateModel.query.filter_by(id=id).scalar()

        if template is None:
            return success_patcher({"msg": "No such template exists."}, 0), 400

        if name is None and check_list is None:
            return success_patcher({"msg": "Either change the name or the checkList."}, 0), 400

        if not name is None:
            template.name = name

        if not check_list is None:
            template.empty_template = {"checkList": check_list}

        db.session.commit()

        return success_patcher({"msg": f"Template {id} updated successfully."}, 1), 200

    @jwt_required()
    @only_admin
    def delete(self, id=None):
        if id is None:
            return success_patcher({"msg": "Provide the id of the template you want to edit."}, 0), 400

        template = TemplateModel.query.filter_by(id=id).scalar()

        if template is None:
            return success_patcher({"msg": "No such template exists."}, 0), 400

        db.session.delete(template)
        db.session.commit()

        return success_patcher({"msg": f"Template {id} deleted successfully."}, 1), 200


class KeeperGroups(Resource):
    @jwt_required()
    @only_admin
    def get(self, id=None):
        # /keeperGroups
        if id is None:
            keeper_groups = KeeperGroupModel.query.all()

            return_dict = keeper_group_model_list_to_dict(keeper_groups)
        # /keeperGroups/{id}
        else:
            keeper_group = KeeperGroupModel.query.filter_by(id=id).scalar()

            if keeper_group is None:
                return success_patcher({"msg": "No such keeper group exists"}, 0), 400

            return_dict = keeper_group_model_to_dict(keeper_group)

        return success_patcher(return_dict, 1), 200

    @jwt_required()
    @only_admin
    def post(self, id=None):
        if not id is None:
            return success_patcher({"msg": "No id in POST /keeperGroups."}, 0), 400

        args = create_keeper_group_parser.parse_args()
        name = args["name"]
        room_names = args["rooms"]

        rooms = []
        for room_name in room_names:
            room = RoomModel.query.filter_by(name=room_name).scalar()

            if room is None:
                return success_patcher({"msg": f"Room {room_name} doesn't exist."}, 0), 400
            else:
                rooms.append(room)

        keeper_group = KeeperGroupModel(name)

        for room in rooms:
            room.keeper_groups.append(keeper_group)

        db.session.commit()

        return success_patcher({"id": keeper_group.id}, 1), 200


class Messages(Resource):
    @jwt_required()
    @only_admin
    def get(self, start=None, end=None):
        if start is None or end is None:
            return success_patcher({"msg": "Provide start and end."}, 0), 400

        messages = MessageModel.query.order_by(
            MessageModel.time.desc()).offset(start).limit(end-start+1).all()

        if messages is None:
            return success_patcher({"msg": "No messages found."}, 0), 400

        return_dict = message_model_list_to_dict(messages)

        return success_patcher(return_dict, 1), 200

    @jwt_required()
    @only_keeper
    def post(self, start=None, end=None):
        if not start is None or not end is None:
            return success_patcher({"msg": "No start or end in POST /messages"}, 0), 400
        args = create_message_parser.parse_args()
        text = args["text"]

        message = MessageModel(datetime.now(), text)
        current_user.messages.append(message)

        db.session.commit()

        return success_patcher({"msg": "Message created successfully."}, 1), 200

    @jwt_required()
    @only_admin
    def put(self, id=None):
        if id is None:
            return success_patcher({"msg": "Provide id."}, 0), 400

        message = MessageModel.query.filter_by(id=id).scalar()

        if message is None:
            return success_patcher({"msg": "Message with given id doesn't exist."}, 0), 400

        message.is_read = True
        db.session.commit()

        return success_patcher({"msg": "Message updated successfully."}, 1), 200


api.add_resource(Users, "/users", "/users/<int:id>")
api.add_resource(Rooms, "/rooms",  "/rooms/<int:id>")
api.add_resource(RoomRecords, "/rooms/<int:id>/records")
api.add_resource(Templates, "/templates", "/templates/<int:id>")
api.add_resource(KeeperGroups, "/keeperGroups", "/keeperGroups/<int:id>")
api.add_resource(Messages, "/messages", "/messages/<int:id>",
                 "/messages/<int:start>/<int:end>")

if __name__ == "__main__":
    app.run(debug=True)
