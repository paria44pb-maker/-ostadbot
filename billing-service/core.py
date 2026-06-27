PLANS = {
    "free": 0,
    "vip": 15,
    "pro": 49,
    "elite": 99
}

def get_plan_price(plan):
    return PLANS.get(plan, 0)
