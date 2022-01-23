# import from libs
from flask import Flask
from flask_restful import Api, Resource, abort
import bcrypt
import re


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

db.init_app(app)
app.app_context().push()
db.create_all()

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


#class Login(Resource):


api.add_resource(Register, "/user/register")

if __name__ == "__main__":
    app.run(debug=True)
