def create_invoice(user_id, amount):
    return {
        "user": user_id,
        "amount": amount,
        "status": "pending"
    }
