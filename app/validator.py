def register_data(json_data):
    if not(json_data['username'] and len(json_data['username'])<30):
        return False
    if not(json_data['password'] and len(json_data['password'])<20):
        return False
    if not(json_data['confirm_password'] and len(json_data['confirm_password'])<20):
        return False
    if json_data['password'] != json_data['confirm_password']:
        return False
        
    return True


def new_advert(json_data):
    return True


def new_comment(json_data):
    return True