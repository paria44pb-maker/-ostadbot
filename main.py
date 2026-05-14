import requests
import socket
import dns.resolver
import os

# =========================
# Force IPv4 (حل مشکل Railway)
# =========================

old_getaddrinfo = socket.getaddrinfo

def force_ipv4(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [r for r in responses if r[0] == socket.AF_INET]

socket.getaddrinfo = force_ipv4

# =========================
# DNS Resolver (Google DNS)
# =========================

def resolve_dns():
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '1.1.1.1']

        answer = resolver.resolve("api.nobitex.ir")

        for rdata in answer:
            print("Resolved IP:", rdata)

    except Exception as e:
        print("DNS Resolve Error:", e)


# =========================
# Nobitex Config
# =========================

API_KEY = os.getenv("NOBITEX_API_KEY")

headers = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type": "application/json"
}

# =========================
# Test Market API
# =========================

def get_market_stats():

    try:

        url = "https://api.nobitex.ir/market/stats"

        r = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        print("STATUS:", r.status_code)
        print("DATA:", r.text[:1000])

    except Exception as e:

        print("❌ Connection Error:", e)


# =========================
# Wallet Balance
# =========================

def get_wallet():

    try:

        url = "https://api.nobitex.ir/users/wallets/balance"

        r = requests.post(
            url,
            headers=headers,
            timeout=20
        )

        print("STATUS:", r.status_code)
        print("WALLET:", r.text)

    except Exception as e:

        print("❌ Wallet Error:", e)


# =========================
# Run
# =========================

if __name__ == "__main__":

    print("Starting Nobitex connection test...")

    resolve_dns()

    get_market_stats()

    get_wallet()
