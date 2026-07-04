class SignalEngine:
    """
    Generates basic trading signals (MVP version)
    """

    def analyze_price(self, price_data: dict):
        """
        Simple logic placeholder
        """

        if price_data.get("change", 0) > 2:
            return {
                "signal": "BUY",
                "strength": "HIGH"
            }

        if price_data.get("change", 0) < -2:
            return {
                "signal": "SELL",
                "strength": "HIGH"
            }

        return {
            "signal": "HOLD",
            "strength": "LOW"
        }
