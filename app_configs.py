from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

import app_secrets
from models.shared import db
from models.user_model import UserModel

app = Flask(__name__)
api = Api(app)

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
    user=app_secrets.SECRETS['postgresUser'], pw=app_secrets.SECRETS['postgresPass'], url=app_secrets.SECRETS['postgresUrl'], db=app_secrets.SECRETS['postgresDb'])

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config["JWT_SECRET_KEY"] = app_secrets.SECRETS["jwt_secret"]
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
# FOR PRODUCTION
#app.config["JWT_COOKIE_SECURE"] = True

db.init_app(app)
app.app_context().push()
migrate = Migrate(app, db)
# db.create_all()

jwt = JWTManager(app)


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserModel.query.filter_by(id=identity).one_or_none()
