from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, get_jwt, create_access_token, set_access_cookies, get_jwt_identity
from datetime import timedelta, datetime

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
# TODO: expiration time for jwt tokens are set to 3 days. Should be discussed.
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=3)

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


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now()
        # If there's a day left for the token to expire issue new token. TODO: disccuss this also.
        target_timestamp = datetime.timestamp(now + timedelta(days=1))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response
