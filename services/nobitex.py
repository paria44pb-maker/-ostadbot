import requests

def get_nobitex_price(symbol="usdt-irr"):
    try:
        url = "https://api.nobitex.ir/market/stats"
        params = {"srcCurrency": symbol.split("-")[0],
                  "dstCurrency": symbol.split("-")[1]}
        
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        # بررسی خطا از سمت نوبیتکس
        if "stats" not in data:
            return None
        
        price = data["stats"][symbol]["bestSell"]
        return price

    except Exception as e:
        print(f"Nobitex error → {e}")
        return None
      
