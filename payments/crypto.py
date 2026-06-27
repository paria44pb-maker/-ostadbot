def create_invoice(user_id, plan):
    return {
        "wallet": "TRC20_ADDRESS",
        "amount": {
            "vip": 10,
            "pro": 25,
            "elite": 50
        }[plan],
        "status": "pending"
    }
