import requests
import pyotp
import time

class NobitexClient:
    def __init__(self, api_key, two_factor_secret):
        self.api_key = api_key
        self.totp = pyotp.TOTP(two_factor_secret)
        self.session = requests.Session()
        self.token = None
        self.token_expiry = 0

    def _get_valid_token(self):
        if time.time() < self.token_expiry:
            return self.token
        headers = {'Authorization': f'Token {self.api_key}', 'X-TOTP': self.totp.now()}
        response = self.session.post('https://api.nobitex.ir/auth/token/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            self.token_expiry = time.time() + 30*24*60*60  # 30 روز
            return self.token
        raise Exception(f"خطا در دریافت توکن: {response.text}")

    def get_price(self, symbol='BTCUSDT'):
        token = self._get_valid_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.session.post('https://api.nobitex.ir/market/stats', json={'srcCurrency': symbol[:3], 'dstCurrency': symbol[3:]}, headers=headers)
        return response.json() if response.status_code == 200 else None
