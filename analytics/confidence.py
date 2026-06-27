def final_confidence(ai_score, smc_score, market_score):
    return (ai_score * 0.4) + (smc_score * 0.4) + (market_score * 0.2)
