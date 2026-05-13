# news_streamer.py
# دریافت و تحلیل اولیه اخبار کریپتو

crypto_keywords_positive = [
    "ETF",
    "Bullish",
    "Adoption",
    "Partnership",
    "Pump"
]

crypto_keywords_negative = [
    "Hack",
    "Ban",
    "Crash",
    "Dump",
    "Liquidation"
]


def analyze_news(news_text):
    """
    تحلیل ساده احساسات خبر
    """

    score = 0

    for word in crypto_keywords_positive:
        if word.lower() in news_text.lower():
            score += 1

    for word in crypto_keywords_negative:
        if word.lower() in news_text.lower():
            score -= 1

    return score


# تست
if __name__ == "__main__":

    sample_news = "Bitcoin ETF approved and market looks bullish"

    sentiment = analyze_news(sample_news)

    print("News Sentiment:", sentiment)
