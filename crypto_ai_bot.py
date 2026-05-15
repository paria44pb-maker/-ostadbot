import os
import requests

# ==========================
# CONFIG
# ==========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# ==========================
# GET CRYPTO PRICE
# ==========================

def get_crypto_price(symbol="bitcoin"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    r = requests.get(url)
    data = r.json()
    return data[symbol]["usd"]

# ==========================
# AI REQUEST (Groq)
# ==========================

def ask_groq(prompt):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(url, headers=headers, json=data)
    result = r.json()

    return result["choices"][0]["message"]["content"]

# ==========================
# AI REQUEST (DeepSeek)
# ==========================

def ask_deepseek(prompt):

    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(url, headers=headers, json=data)
    result = r.json()

    return result["choices"][0]["message"]["content"]

# ==========================
# MAIN BOT
# ==========================

def main():

    price = get_crypto_price("bitcoin")

    print("BTC Price:", price)

    prompt = f"""
    Bitcoin current price is {price} USD.
    Give a short trading analysis.
    """

    print("\n--- Groq Analysis ---")
    print(ask_groq(prompt))

    print("\n--- DeepSeek Analysis ---")
    print(ask_deepseek(prompt))


if __name__ == "__main__":
    main()
