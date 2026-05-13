# risk_manager.py
# مدیریت سرمایه و حجم معامله

def position_size(balance, risk_percent, stop_loss_percent):
    """
    balance: کل سرمایه
    risk_percent: درصد ریسک هر معامله
    stop_loss_percent: فاصله استاپ
    """

    risk_amount = balance * risk_percent

    position = risk_amount / stop_loss_percent

    return round(position, 4)


def kelly_criterion(win_rate, risk_reward):
    """
    win_rate: درصد برد
    risk_reward: نسبت سود به ضرر
    """

    kelly = win_rate - ((1 - win_rate) / risk_reward)

    return max(kelly, 0)
