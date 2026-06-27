import hmac
import hashlib
import os

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change_me")

def verify_telegram_signature(body: bytes, header_signature: str):
    if not header_signature:
        return False

    secret = WEBHOOK_SECRET.encode()
    hash_obj = hmac.new(secret, body, hashlib.sha256).hexdigest()

    return hmac.compare_digest(hash_obj, header_signature)
