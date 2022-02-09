# 1 for successful, 0 for error
from tabnanny import check
from models.user_model import UserType
from models.room_model import RoomModel
from models.template_model import TemplateModel


def success_patcher(dict, number):
    dict["success"] = number
    return dict


def room_model_to_dict(room):
    return_dict = {
        "id": room.id,
        "name": room.name,
        "status": room.status.value,
        "checkList": room.template.empty_template["checkList"]
    }
    return {"room": return_dict}


def room_model_list_to_dict(rooms):
    arr = []
    for room in rooms:
        temp_dict = {
            "id": room.id,
            "name": room.name,
            "status": room.status.value
        }
        arr.append(temp_dict)
    return_dict = {
        "rooms": arr
    }
    return return_dict


def template_model_to_dict(template):
    return_dict = {
        "template": {
            "id": template.id,
            "name": template.name,
            "checkList": template.empty_template,
        }
    }
    return return_dict


def template_model_list_to_dict(templates):
    arr = []
    for template in templates:
        temp_dict = {
            "id": template.id,
            "name": template.name,
            "checkList": template.empty_template
        }
        arr.append(temp_dict)
    return_dict = {
        "templates": arr
    }
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


# Checks if the check list is made from template
def is_check_list_for_room(room, check_list):
    template = room.template

    for item in check_list.keys():
        if not item in template.empty_template["checkList"]:
            return False
    return True and len(template.empty_template["checkList"]) == len(check_list.keys())


# Checks if the check list items in the record are assigned proper values.
def check_item_values(check_list):
    for value in check_list.values():
        if value != 2 and value != 3 and value != 4:
            return False
    return True
