alerts = {}

def set_alert(user_id, price):
    alerts[user_id] = price

def check_alert(current_price):

    triggered = []

    for user,price in alerts.items():
        if current_price >= price:
            triggered.append(user)

    return triggered
