def detect_structure(data):
    return {
        "BOS": True,
        "CHOCH": False,
        "liquidity_zone": "above",
        "fvg": True
    }

def smc_score(structure):
    score = 0

    if structure["BOS"]:
        score += 30
    if structure["fvg"]:
        score += 25
    if structure["CHOCH"]:
        score += 20

    return score
