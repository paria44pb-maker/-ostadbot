from ai.groq import ask_groq

async def route_analysis(market_data):
    prompt = f"""
    Analyze this crypto market using:
    - Trend
    - Liquidity
    - Smart Money (BOS, CHOCH, FVG)
    - Volume
    - Risk

    Return JSON:
    signal, confidence, entry, sl, tp
    Data: {market_data}
    """

    return await ask_groq(prompt)
