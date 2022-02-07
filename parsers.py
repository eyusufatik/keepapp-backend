from flask_restful import reqparse
from datetime import datetime

# parser for registration form
user_registration_parser = reqparse.RequestParser()
user_registration_parser.add_argument(
    "userType", type=int, help="0 for super admin, 1 for company admin, 2 for keeper", required=True)
user_registration_parser.add_argument(
    "username", type=str, help="Provide username", required=True)
user_registration_parser.add_argument(
    "password", type=str, help="Provide password", required=True)


# parser for login form
user_login_parser = reqparse.RequestParser()
user_login_parser.add_argument(
    "username", type=str, help="Provide username", required=True)
user_login_parser.add_argument(
    "password", type=str, help="Provide password.", required=True)

# parser for room creation
create_room_parser = reqparse.RequestParser()
create_room_parser.add_argument(
    "name", type=str, help="Provide a name for the room", required=True)
create_room_parser.add_argument("keeperGroupId", type=int, required=False)
create_room_parser.add_argument(
    "checkList", type=str, action="append", required=False)
create_room_parser.add_argument("templateId", type=int, required=False)

# parser for date in /rooms/<id>/records?date=YYYY-MM-DD
date_in_query_parser = reqparse.RequestParser()
date_in_query_parser.add_argument("date", type=lambda x: datetime.strptime(
    x, '%Y-%m-%d'), help="Date should be in YYYY-MM-DD format", required=False)
