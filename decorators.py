from models.user_model import UserType
from flask_jwt_extended import current_user
from util_funcs import success_patcher

def only_admin(func):
    """
    Allows routes to be called if the user is an admin or a super admin.
    """
    def check_user(*argv, **kwargs):
        if current_user.user_type == UserType.admin or current_user.user_type == UserType.super_admin:
           returned_value = func(*argv, **kwargs)
           return returned_value
        else:
            return success_patcher({"msg": "Only admins can call this URL."}, 0), 400
    return check_user

def only_keeper(func):
    """
    Allows routes to be called if the user is a keeper.
    """
    def check_user(*argv, **kwargs):
        if current_user.user_type == UserType.keeper:
           returned_value = func(*argv, **kwargs)
           return returned_value
        else:
            return success_patcher({"msg": "Only keepers can call this URL."}, 0), 400
    return check_user