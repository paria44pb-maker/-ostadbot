users = {}

def create_user(user_id):
    users[user_id] = {
        "plan": "free",
        "balance": 0,
        "signals_used": 0
    }
