# 1 for successful, 0 for error
from tabnanny import check
from models.user_model import UserType
from models.room_model import RoomModel, RoomStatus
from models.template_model import TemplateModel
from models.keeper_group_model import KeeperGroupModel


def success_patcher(dict, number):
    """
    Patches a "success":1/0 field to the return dictionary.

    :param dict: Response dictionary.
    :param number: 1 for successfull, 0 for unsuccessfull.
    """
    dict["success"] = number
    return dict


def user_model_to_dict(user):
    """
    {
        "user": {
            "id": 5,
            "username": "testKeeper",
            "userType": 2,
            "keeperGroups": [
                {
                    "id": 1,
                    "name": "group A",
                    "rooms": [
                        "room 102",
                        "VK510"
                    ],
                    "keeperIds": [
                        5
                    ]
                }
            ],
            "records": [
                {
                    "id": 14,
                    "roomId": 13,
                    "time": "2022-02-08 16:56:09.139746",
                    "keeperId": 5,
                    "checkList": {
                        "yatak": 3,
                        "televizyon": 2,
                        "kettle": 4
                    },
                    "notes": "Misafir yatağa sıçmış.",
                    "photos": [
                        "example.com/example.jpg",
                        "example.com/example2.jpg"
                    ]
                }
            ],
            "messages": [
                {
                    "id": 3,
                    "senderId": 5,
                    "time": "2022-02-14 20:18:06.498534",
                    "message": "Postmanden deneme",
                    "is_read": false
                }
            ]
        },
        "success": 1
    }
    """
    return_dict = {}

    if user.user_type == UserType.admin:
        return_dict = {
            "user": {
                "id": user.id,
                "username": user.username,
                "userType": user.user_type,
            }
        }
    elif user.user_type == UserType.keeper:
        return_dict = {
            "user":{
                "id": user.id,
                "username": user.username,
                "userType": user.user_type,
                "keeperGroups": keeper_group_model_list_to_dict(user.keeper_groups)["keeperGroups"],
                "records": record_model_list_to_dict(user.records)["records"],
                "messages": message_model_list_to_dict(user.messages)["messages"]
            }
        }

    return return_dict


def user_model_list_to_dict(users):
    arr = []
    for user in users:
        temp_dict = user_model_to_dict(user)["user"]
        arr.append(temp_dict)
    return {"users": arr}


def room_model_to_dict(room):
    """
    {
        "room": {
            "id": 2,
            "name": "VK707",
            "status": 1,
            "checkList": [
                "yatak",
                "televizyon",
                "kettle"
            ]
        },
        "success": 1
    }
    """
    return_dict = {
        "room": {
            "id": room.id,
            "name": room.name,
            "status": room.status.value,
            "checkList": room.template.empty_template["checkList"]
        }
    }
    return return_dict


def room_model_list_to_dict(rooms):
    arr = []
    for room in rooms:
        temp_dict = room_model_to_dict(room)["room"]
        arr.append(temp_dict)
    return_dict = {
        "rooms": arr
    }
    return return_dict


def template_model_to_dict(template):
    """
    {
        "template": {
            "id": 10,
            "name": "atikali 2+1",
            "checkList": [
                "yastık",
                "tepsi",
                "sehpa"
            ]
        },
        "success": 1
    }
    """
    return_dict = {
        "template": {
            "id": template.id,
            "name": template.name,
            "checkList": template.empty_template["checkList"]
        }
    }
    return return_dict


def template_model_list_to_dict(templates):
    arr = []
    for template in templates:
        temp_dict = template_model_to_dict(template)["template"]
        arr.append(temp_dict)
    return_dict = {
        "templates": arr
    }
    return return_dict


def keeper_group_model_to_dict(keeper_group):
    """
    {
        "keeperGroup": {
            "id": 1,
            "name": "group A",
            "rooms": [
                "room 102",
                "VK510"
            ],
            "keeperIds": [
                5
            ]
        },
        "success": 1
    }
    """
    return_dict = {
        "keeperGroup": {
            "id": keeper_group.id,
            "name": keeper_group.name,
            "rooms": [x.name for x in keeper_group.rooms],
            "keeperIds": [x.id for x in keeper_group.keepers]
        }
    }
    return return_dict


def keeper_group_model_list_to_dict(keeper_groups):
    arr = []
    for keeper_group in keeper_groups:
        temp_dict = keeper_group_model_to_dict(keeper_group)["keeperGroup"]
        arr.append(temp_dict)
    return_dict = {
        "keeperGroups": arr
    }
    return return_dict


def message_model_to_dict(message):
    """
    {
        "message": {
                "id": 8,
                "senderId": 5,
                "time": "2022-02-14 21:32:43.455488",
                "message": "Postmanden 4",
                "is_read": false
        }
        ,
        "success": 1
    }
    """
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
        temp_dict = message_model_to_dict(message)["message"]
        arr.append(temp_dict)

    return_dict = {
        "messages": arr
    }

    return return_dict


def record_model_to_dict(record):
    """
    {
        "record": {
            "checkList": {
                "yatak": 4,
                "kettle": 4,
                "televizyon": 2
            },
            "notes": "Misafir yatağa sıçmış.",
            "photos": [
                "example.com/example.jpg",
                "example.com/example2.jpg"
            ]
        },
        "success": 1
    }
    """
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
        temp_dict = record_model_to_dict(record)["record"]
        arr.append(temp_dict)

    return_dict = {
        "records": arr
    }

    return return_dict


def check_room_access(user, room):
    """
    Checks if the user has access to the room. 
    Admins and super admins can "access" every room. 
    Keepers can only access a room if the account is in a keeper group that can access the room.
    """
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
    """
    Checks if the sent checkList is made up from solely the rooms template.
    Fields (a.k.a. items) not originally in the template will cause the function to return false. 

    :param room: Room the check_list is submitted for.
    :param check_list: Check list
    """
    template = room.template

    for item in check_list.keys():
        if not item in template.empty_template["checkList"]:
            return False
    return len(template.empty_template["checkList"]) == len(check_list.keys())


# Checks if the check list items in the record are assigned proper values.
def check_item_values(check_list):
    """
    In a check list, checks if every item is missing/damaged/ok.
    Values other than 2 3 or 4 will cause the function to return false.
    """
    for value in check_list.values():
        if value != 2 and value != 3 and value != 4:
            return False
    return True


# Checks item status in the check list and returns RoomStatus
def get_room_status_from_check_list(check_list):
    """
    From item status in the check list, derives the room status.
    See also: models.room_model.RoomStatus
    """
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
        return_val = 3

    return RoomStatus(return_val)
