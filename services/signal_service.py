from services.nobitex_service import get_prices

def generate_signal():

    prices = get_prices()
    btc = prices["btc"]

    if btc == 0:
        return "خطا در دریافت قیمت"

    if btc % 2 == 0:
        signal = "BUY"
    else:
        signal = "HOLD"

    return f"""
سیگنال بازار BTC

قیمت: {btc}

پیشنهاد:
{signal}
"""
