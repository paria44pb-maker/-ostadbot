import time

user_last = {}

def check(user_id):
    now = time.time()
    if user_id in user_last and now - user_last[user_id] < 2:
        return False
    user_last[user_id] = now
    return True
