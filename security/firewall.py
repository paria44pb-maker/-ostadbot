def check_request(ip):
    blocked = ["spam_ip"]
    if ip in blocked:
        return False
    return True
