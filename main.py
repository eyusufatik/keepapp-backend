# import from libs
from datetime import datetime
from hashlib import new
from inspect import currentframe
from tabnanny import check
from flask import Flask, jsonify
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_jwt_extended import create_access_token, current_user, jwt_required, JWTManager, set_access_cookies, unset_jwt_cookies
import bcrypt

# import from own code
import config
from models.user_model import UserModel, UserType
from models.message_model import MessageModel
from models.keeper_group_model import KeeperGroupModel
from models.room_model import RoomModel, RoomStatus
from models.template_model import TemplateModel
from models.record_model import RecordModel
from models.shared import db
from parsers import *
from util_funcs import *

app = Flask(__name__)
api = Api(app)

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
    user=config.CONFIG['postgresUser'], pw=config.CONFIG['postgresPass'], url=config.CONFIG['postgresUrl'], db=config.CONFIG['postgresDb'])

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config["JWT_SECRET_KEY"] = config.CONFIG["jwt_secret"]
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
# FOR PRODUCTION
#app.config["JWT_COOKIE_SECURE"] = True

db.init_app(app)
app.app_context().push()
migrate = Migrate(app, db)
# db.create_all()

jwt = JWTManager(app)

# --START-- decoratorler ayrı bir dosyada
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserModel.query.filter_by(id=identity).one_or_none()


def only_admin(func):
    def check_user(*argv, **kwargs):
        if current_user.user_type == UserType.admin or current_user.user_type == UserType.super_admin:
           returned_value = func(*argv, **kwargs)
           return returned_value
        else:
            return success_patcher({"msg": "User is not authorized to create a room"}, 0), 400 # 401 + burada daha generic bir mesaj verilmesi lazım. Onlyadmin routelarda tutması için "Not authorized." yeterli gibi.
    return check_user
# --END--

@app.route("/user/register", methods=["POST"])
def register():
    args = user_registration_parser.parse_args()
    user_type = UserType(args["userType"]) #bu userType body ile gelmeyecek. Userlar hep keeper, sadece biz admin oluşturabiliriz.
    username = args["username"]
    password = args["password"]
    if len(password) < 8:
        return success_patcher({"msg": "Password must be at least 8 characters."}, 0), 400 #422 sanki, 400 daha bozuk gelen json için falan.

    if UserModel.query.filter_by(username=username).count() > 0:
        return success_patcher({"msg": "User already exists"}, 0), 409 # 409 iyiymiş, 403 kullanıyordum.
    else:
        hashed_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user = UserModel(user_type,
                         username, hashed_pass.decode())
        db.session.add(user)
        db.session.commit()
        return success_patcher({}, 1), 201 #msg + user_id hojdur.


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
            return jsonify(success_patcher({"msg": "Invalid username or password"}, 0)), 400 # 401(?).
    else:
        return jsonify(success_patcher({"msg": "Invalid username or password"}, 0)), 400  # user does not exists, 401.


@app.route("/user/logout", methods=["GET"])
def logout_with_cookies():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


class UserRooms(Resource):
    @jwt_required()
    def get(self):
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


class Room(Resource):
    @jwt_required()
    def get(self, id):
        room = RoomModel.query.filter_by(id=id).scalar()

        if room is None:
            return success_patcher({"msg": "Room with given ID doesn't exist."}, 0), 400 # 404

        if current_user.user_type == UserType.keeper and not check_room_access(current_user, room):
            return success_patcher({"msg": "Keeper doesn't have access to the room, add it to a group that has access to the room"}, 0), 400 #401 Not Authorized. yeterli 

        room_dict = room_model_to_dict(room)
        return success_patcher(room_dict, 1), 200
    # en alta detaylı not bıraktım. Buradan sonrasına bakmadım.
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


class RoomRecord(Resource):
    @jwt_required()
    def get(self, id):
        room = RoomModel.query.filter_by(id=id).scalar()

        if room is None:
            return success_patcher({"msg": "Room with given ID doesn't exist."}, 0), 400

        if check_room_access(current_user, room):
            todays_record = RecordModel.query.filter_by(room_id=id).filter(
                RecordModel.time <= datetime.now()).filter(datetime.today().date() <= RecordModel.time).scalar()

            if todays_record is None:
                return success_patcher({"msg": "No record today for the room."}, 0), 400

            return_dict = {}
            return_dict["checkList"] = todays_record.filled_list
            return_dict["notes"] = todays_record.notes
            return_dict["photos"] = todays_record.photos
            return_dict = {"record": return_dict}

            return success_patcher(return_dict, 1), 200

        else:
            return success_patcher({"msg": "User doesn't have access to the room"}, 0), 400

    def post(self, id):
        pass


api.add_resource(UserRooms, "/user/rooms") #user/rooms dublicate + not rest oluyor. rooms'a get yaptığında o kontrolü içeride yapacağız. Admin değilse ona göre çekecek.
api.add_resource(Room, "/room", "/room/<int:id>")
api.add_resource(RoomRecord, "/room/<int:id>/record") 
# Burada da room record diye ayrı bir route değil de
# rooms.get -> userType+yetki alanı göre odaları görme || rooms/:id.get(date?) -> yalnız odanın kaydı. date varsa o günkü kaydı. || rooms.post(array of room_numbers, template name || checklist json) -> Oluştur, çelişen oda varsa üstüne yazabilir, bunu düşünmek lazım.
# rooms/:id.post(data in body) -> o günkü checklist verileri.
# tbc
if __name__ == "__main__":
    app.run(debug=True)
