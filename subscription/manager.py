import time

PLANS = {
    "free": 0,
    "vip": 10,
    "pro": 25,
    "elite": 50
}

users = {}

def set_plan(user_id, plan):
    users[user_id] = {
        "plan": plan,
        "expire": time.time() + 30 * 86400
    }

def check_access(user_id):
    u = users.get(user_id)
    if not u:
        return "free"
    if time.time() > u["expire"]:
        return "free"
    return u["plan"]
