# import from libs
from flask import Flask, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token, current_user, jwt_required, JWTManager, set_access_cookies
import bcrypt

# import from own code
import config
from models.user_model import UserModel, UserType
from models.shared import db
from parsers import *
from util_funcs import *

app = Flask(__name__)
api = Api(app)

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
    user=config.CONFIG['postgresUser'], pw=config.CONFIG['postgresPass'], url=config.CONFIG['postgresUrl'], db=config.CONFIG['postgresDb'])

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config["JWT_SECRET_KEY"] = config.CONFIG["jwt_secret"]
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
# FOR PRODUCTION
#app.config["JWT_COOKIE_SECURE"] = True  

db.init_app(app)
app.app_context().push()
db.create_all()

jwt = JWTManager(app)

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.user_id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserModel.query.filter_by(user_id=identity).one_or_none()

class Register(Resource):
    def post(self):
        args = user_registration_parser.parse_args()
        user_type = UserType(args["userType"])
        username = args["username"]
        password = args["password"]
        if len(password) < 8:
            return success_patcher({"response": "Password must be at least 8 characters."}, 0), 400

        if UserModel.query.filter_by(username=username).count() > 0:
            return success_patcher({"response": "User already exists"}, 0), 409
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
            response = success_patcher({"response": "Logged in successfully"}, 1)
            access_token = create_access_token(identity=user_from_db)
            response = jsonify(response)
            set_access_cookies(response, access_token)
            return response, 200
        else:
            return jsonify(success_patcher({"response": "Invalid username or password"}, 0)), 400
    else:
        return jsonify(success_patcher({"response": "Invalid username or password"}, 0)), 400


api.add_resource(Register, "/user/register")

if __name__ == "__main__":
    app.run(debug=True)
