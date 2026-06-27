users = {}

def get_user(user_id):
    return users.get(user_id, {"plan": "free"})
