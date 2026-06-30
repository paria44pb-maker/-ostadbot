#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Entry Point
ربات هوشمند تحلیل و سیگنال ارزهای دیجیتال
"""

import os
import sys
import uvicorn

# ============================================================
#                    IMPORT ALL PARTS
# ============================================================

from part1 import *
from part2 import *
from part3 import *
from part4 import *
from part5 import *
from part6 import *
from part7 import *
from part8 import *
from part9 import *
from part10 import *
from part11 import *
from part12 import *
from part13 import *
from part14 import *
from part15 import *

# ============================================================
#                    CONFIG
# ============================================================

try:
    from part2 import PORT
except:
    PORT = int(os.environ.get("PORT", 8080))

# ============================================================
#                    RUN
# ============================================================

if __name__ == "__main__":
    print("🚀 Starting CryptoPulse AI Bot v3.0...")
    print("📁 All 15 parts imported successfully!")
    print(f"🌐 Server running on port {PORT}")
    
    uvicorn.run(
        "bot:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
