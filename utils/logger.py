import datetime


def log_event(message):

    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{time}] {message}")
