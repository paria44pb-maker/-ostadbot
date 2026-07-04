"""
═══════════════════════════════════════════════════════════════════════
CryptoPulse AI Enterprise
Core Constants

Author : CryptoPulse Team
Version: 10.0.0 Enterprise
Python : 3.11+

Description:
Global immutable constants used across the entire application.

DO NOT put configuration values here.
Environment-specific settings belong in config/settings.py.

═══════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

# ==========================================================
# PROJECT
# ==========================================================

PROJECT_NAME: str = "CryptoPulse AI"

PROJECT_SLUG: str = "cryptopulse-ai"

PROJECT_DESCRIPTION: str = (
    "Enterprise AI Cryptocurrency Trading Platform"
)

VERSION: str = "10.0.0"

BUILD_NUMBER: int = 1

AUTHOR: str = "CryptoPulse Team"

COPYRIGHT: str = "Copyright © CryptoPulse"

LICENSE: str = "Proprietary"

PYTHON_MIN_VERSION = (3, 11)

# ==========================================================
# ROOT PATHS
# ==========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

CORE_DIR = ROOT_DIR / "core"

CONFIG_DIR = ROOT_DIR / "config"

DATABASE_DIR = ROOT_DIR / "database"

LOG_DIR = ROOT_DIR / "logs"

BACKUP_DIR = ROOT_DIR / "backup"

CACHE_DIR = ROOT_DIR / "cache"

TEMP_DIR = ROOT_DIR / "temp"

DATA_DIR = ROOT_DIR / "data"

TEST_DIR = ROOT_DIR / "tests"

# ==========================================================
# NETWORK
# ==========================================================

DEFAULT_TIMEOUT = 30

CONNECT_TIMEOUT = 10

READ_TIMEOUT = 30

WRITE_TIMEOUT = 30

MAX_RETRY = 5

RETRY_DELAY = 2

MAX_CONCURRENT_REQUESTS = 100

# ==========================================================
# CACHE
# ==========================================================

CACHE_TTL = 60

MARKET_CACHE_TTL = 5

PRICE_CACHE_TTL = 2

ORDERBOOK_CACHE_TTL = 1

# ==========================================================
# TELEGRAM
# ==========================================================

TELEGRAM_MESSAGE_LIMIT = 4096

TELEGRAM_CAPTION_LIMIT = 1024

CALLBACK_DATA_LIMIT = 64

# ==========================================================
# DATABASE
# ==========================================================

DEFAULT_POOL_SIZE = 20

MAX_OVERFLOW = 30

POOL_TIMEOUT = 30

POOL_RECYCLE = 3600

# ==========================================================
# ANALYSIS
# ==========================================================

DEFAULT_SYMBOL = "BTCUSDT"

DEFAULT_TIMEFRAME = "1h"

MAX_CANDLES = 5000

MIN_CANDLES = 300

# ==========================================================
# RISK
# ==========================================================

DEFAULT_RISK_PERCENT = 2.0

MAX_DAILY_LOSS = 10.0

MAX_OPEN_POSITIONS = 5

DEFAULT_LEVERAGE = 1

# ==========================================================
# AI
# ==========================================================

AI_MAX_TOKENS = 4096

AI_TEMPERATURE = 0.2

AI_TOP_P = 0.9

# ==========================================================
# LOGGING
# ==========================================================

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ==========================================================
# APPLICATION STATES
# ==========================================================


class AppState(str, Enum):
    STARTING = "STARTING"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    MAINTENANCE = "MAINTENANCE"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    CRASHED = "CRASHED"


# ==========================================================
# SIGNAL TYPES
# ==========================================================


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


# ==========================================================
# POSITION SIDE
# ==========================================================


class PositionSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


# ==========================================================
# ORDER STATUS
# ==========================================================


class OrderStatus(str, Enum):
    NEW = "NEW"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


# ==========================================================
# SUPPORTED TIMEFRAMES
# ==========================================================

SUPPORTED_TIMEFRAMES = (
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "12h",
    "1d",
    "1w",
    "1M",
)

# ==========================================================
# HEALTH STATUS
# ==========================================================


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


# ==========================================================
# EXIT CODES
# ==========================================================

EXIT_SUCCESS = 0

EXIT_ERROR = 1

EXIT_CONFIG_ERROR = 2

EXIT_DATABASE_ERROR = 3

EXIT_NETWORK_ERROR = 4

EXIT_FATAL_ERROR = 99
