# 1 for successful, 0 for error
from models.user_model import UserType


def success_patcher(dict, number):
    dict["success"] = number
    return dict


def room_model_to_dict(room):
    return_dict = {}
    return_dict["id"] = room.id
    return_dict["name"] = room.name
    return_dict["status"] = room.status.value
    return_dict["checkList"] = room.template.empty_template["checkList"]
    return {"room":return_dict}


def room_model_list_to_dict(rooms):
    arr = []
    for room in rooms:
        temp_dict = {}
        temp_dict["id"] = room.id
        temp_dict["name"] = room.name
        temp_dict["status"] = room.status.value
        arr.append(temp_dict)
    return_dict = {}
    return_dict["rooms"] = arr
    return return_dict


def check_room_access(user, room):
    if user.user_type == UserType.super_admin or user.user_type == UserType.admin:
        return True
    else:
        for group in room.keeper_groups:
            print(group)
            if user in group.keepers:
                return True
        return False
