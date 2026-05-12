def analyze_market(price, change_percent):

    trend = "Bullish" if float(change_percent) > 0 else "Bearish"

    if abs(float(change_percent)) < 1:
        momentum = "Weak"
    elif abs(float(change_percent)) < 3:
        momentum = "Moderate"
    else:
        momentum = "Strong"

    return {
        "trend": trend,
        "momentum": momentum
    }
  
