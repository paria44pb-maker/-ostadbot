def create_payment(user_id, plan):
    return {
        "user": user_id,
        "plan": plan,
        "wallet": "TRC20_ADDRESS",
        "status": "waiting"
    }
