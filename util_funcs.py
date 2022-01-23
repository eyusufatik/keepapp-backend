# 1 for successful, 0 for error
def success_patcher(dict, number):
    dict["success"] = number
    return dict