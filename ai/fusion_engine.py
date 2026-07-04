from ai.groq_engine import GroqAI
from signals.advanced_signal_engine import AdvancedSignalEngine


class FusionEngine:
    """
    Combines AI + Technical Analysis
    """

    def __init__(self):
        self.ai = GroqAI()
        self.ta = AdvancedSignalEngine()

    # =========================
    # 🧠 FINAL DECISION ENGINE
    # =========================
    def analyze_market(self, prices):
        ta_result = self.ta.analyze(prices)

        ai_prompt = f"""
        Market analysis:
        Signal: {ta_result['signal']}
        Score: {ta_result['score']}
        Prices: {prices[-5:]}

        Should we BUY, SELL or HOLD?
        """

        ai_response = self.ai.ask(ai_prompt)

        return {
            "technical": ta_result,
            "ai": ai_response
        }
