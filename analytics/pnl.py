def calculate_revenue(users):
    vip = users.get("vip", 0)
    pro = users.get("pro", 0)

    return (vip * 15) + (pro * 49)
