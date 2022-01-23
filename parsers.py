from flask_restful import reqparse

user_registration_parser = reqparse.RequestParser()
user_registration_parser.add_argument(
    "companyName", type=str, help="Name of the personnel's company", required=True)
user_registration_parser.add_argument(
    "userType", type=int, help="0 for super admin, 1 for company admin, 2 for keeper", required=True)
user_registration_parser.add_argument(
    "username", type=str, help="Username of the personnel", required=True)
user_registration_parser.add_argument(
    "password", type=str, help="Password of the personnel", required=True)