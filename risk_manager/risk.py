def calculate_risk(balance, confidence):
    if confidence < 40:
        return "NO TRADE"

    risk = balance * 0.02
    return risk
