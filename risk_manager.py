def calculate_risk(entry, stop):

    risk = abs(entry - stop)

    tp1 = entry + (risk * 2)

    tp2 = entry + (risk * 3)

    return {
        "risk": round(risk,2),
        "tp1": round(tp1,2),
        "tp2": round(tp2,2)
    }
