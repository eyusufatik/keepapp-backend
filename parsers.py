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


# parser for updating user data
update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument("oldPassword", type=str)
update_user_parser.add_argument("newPassword", type=str)
update_user_parser.add_argument("keeperGroupIds", type=int, action="append")


# parser for room creation
create_room_parser = reqparse.RequestParser()
create_room_parser.add_argument(
    "names", action="append", type=str, help="Provide a name for the room", required=True)
create_room_parser.add_argument(
    "checkList", type=str, action="append", required=False)
create_room_parser.add_argument("templateId", type=int, required=False)


# parser for date in /rooms/<id>/records?date=YYYY-MM-DD
date_in_query_parser = reqparse.RequestParser()
date_in_query_parser.add_argument("date", type=lambda x: datetime.strptime(
    x, '%Y-%m-%d'), help="Date should be in YYYY-MM-DD format", required=False)


# parser for creating a record
create_record_parser = reqparse.RequestParser()
create_record_parser.add_argument(
    "checkList", type=dict, help="'checkList' field must be included in the body.", required=True)
create_record_parser.add_argument("notes", type=str)
create_record_parser.add_argument("photos", type=str, action="append")


# parser for creating a template
create_template_parser = reqparse.RequestParser()
create_template_parser.add_argument(
    "name", type=str, help="Template must have a name", required=True)
create_template_parser.add_argument(
    "checkList", type=str, action="append", help="Template must have a checkList field", required=True)


# parser for updating a template
update_template_parser = reqparse.RequestParser()
update_template_parser.add_argument(
    "name", type=str, help="Template must have a name", required=False)
update_template_parser.add_argument(
    "checkList", type=str, action="append", help="Template must have a checkList field", required=False)


# parser for creating keeper group
create_keeper_group_parser = reqparse.RequestParser()
create_keeper_group_parser.add_argument(
    "name", type=str, help="Keeper group must have a name", required=True)
create_keeper_group_parser.add_argument(
    "rooms", type=str, action="append", help="Provide rooms the group can access to.", required=True)


create_message_parser = reqparse.RequestParser()
create_message_parser.add_argument(
    "text", type=str, help="Message field must not be empty.", required=True)
