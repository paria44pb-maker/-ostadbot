def simple_signal(price_data):
    try:
        price = float(price_data["data"]["ticker"]["last"])
        if price > 50000:
            return "SELL"
        return "BUY"
    except:
        return "HOLD"
