from models.user_model import UserType
from flask_jwt_extended import current_user
from util_funcs import success_patcher

def only_admin(func):
    def check_user(*argv, **kwargs):
        if current_user.user_type == UserType.admin or current_user.user_type == UserType.super_admin:
           returned_value = func(*argv, **kwargs)
           return returned_value
        else:
            return success_patcher({"msg": "User is not authorized to create a room"}, 0), 400
    return check_user

def only_keeper(func):
    def check_user(*argv, **kwargs):
        if current_user.user_type == UserType.keeper:
           returned_value = func(*argv, **kwargs)
           return returned_value
        else:
            return success_patcher({"msg": "User is not authorized to create a room"}, 0), 400
    return check_user