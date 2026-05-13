# logger.py
# سیستم لاگ ساده برای ربات

import datetime


def log(message):

    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    log_message = f"[{now}] {message}"

    print(log_message)

    with open("whalemind.log", "a") as f:
        f.write(log_message + "\n")
