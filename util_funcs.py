# 1 for successful, 0 for error
from tabnanny import check
from models.user_model import UserType
from models.room_model import RoomModel, RoomStatus
from models.template_model import TemplateModel
from models.keeper_group_model import KeeperGroupModel


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


def keeper_group_model_list_to_dict(keeper_groups):
    arr = []
    for keeper_group in keeper_groups:
        temp_dict = {
            "id": keeper_group.id,
            "name": keeper_group.name,
            "rooms": [x.name for x in keeper_group.rooms],
            "keeperIds": [x.id for x in keeper_group.keepers]
        }
        arr.append(temp_dict)
    return_dict = {
        "keeperGroups": arr
    }
    return return_dict


def keeper_group_model_to_dict(keeper_group):
    return_dict = {
        "keeperGroup": {
            "id": keeper_group.id,
            "name": keeper_group.name,
            "rooms": [x.name for x in keeper_group.rooms],
            "keeperIds": [x.id for x in keeper_group.keepers]
        }
    }
    return return_dict


def message_model_to_dict(message):
    return_dict = {
        "message": {
            "id": message.id,
            "senderId": message.sender_id,
            "time": str(message.time),
            "message": message.message,
            "is_read": message.is_read
        }
    }
    return return_dict


def message_model_list_to_dict(messages):
    arr = []
    for message in messages:
        temp_dict = {
            "id": message.id,
            "senderId": message.sender_id,
            "time": str(message.time),
            "message": message.message,
            "is_read": message.is_read
        }
        arr.append(temp_dict)

    return_dict = {
        "messages": arr
    }

    return return_dict


def record_model_to_dict(record):
    return_dict = {
        "record": {
            "id": record.id,
            "roomId": record.room_id,
            "time": str(record.time),
            "keeperId": record.keeper_id,
            "checkList": record.filled_list,
            "notes": record.notes,
            "photos": record.photos
        }
    }
    return return_dict


def record_model_list_to_dict(records):
    arr = []
    for record in records:
        temp_dict = {
            "id": record.id,
            "roomId": record.room_id,
            "time": str(record.time),
            "keeperId": record.keeper_id,
            "checkList": record.filled_list,
            "notes": record.notes,
            "photos": record.photos
        }
        arr.append(temp_dict)

    return_dict = {
        "records": arr
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


# Checks item status in the check list and returns RoomStatus
def get_room_status_from_check_list(check_list):
    has_missing = False
    has_damaged = False

    for value in check_list.values():
        if value == 2:
            has_missing = True
        elif value == 3:
            has_damaged = True

    return_val = 4
    if has_missing and has_damaged:
        return_val = 23
    elif has_missing:
        return_val = 2
    elif has_damaged:
        3

    return RoomStatus(return_val)
