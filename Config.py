import os

# --- API Credentials ---
# It's highly recommended to use environment variables for sensitive information.
# You can set these variables in your deployment environment (e.g., Railway).
# Example: export NOBITEX_API_KEY='your_actual_api_key'
# Example: export NOBITEX_SECRET='your_actual_secret'

NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY", "YOUR_API_KEY_HERE") # Fallback for local testing
NOBITEX_SECRET = os.getenv("NOBITEX_SECRET", "YOUR_SECRET_HERE")   # Fallback for local testing

# Fallback for Groq API key if not set in env
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")

# Fallback for Telegram Token if not set in env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_TOKEN_HERE")

# --- Bot Configuration ---
# Example: Set a default trading pair or other bot-specific settings
DEFAULT_TRADING_PAIR = "btc-rls" # Example: Bitcoin/Rial
INITIAL_BUY_AMOUNT_BTC = 0.0001 # Example: Amount to buy in BTC for testing
INITIAL_BUY_PRICE_RLS = 50000000 # Example: Target buy price in Rial for testing

# --- Other settings ---
# Example: Time delay between API requests to avoid hitting rate limits
API_REQUEST_DELAY = 0.5 # seconds

# Example: Maximum number of retries for API requests
MAX_API_RETRIES = 3

# Example: Initial backoff multiplier for retries
RETRY_DELAY_MULTIPLIER = 2
