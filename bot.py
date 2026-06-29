"""
🦅 OstadBot v10.0 | Main Entry Point
"""
from part1 import *
from part2 import *
from part3 import *
from part4 import *

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=cfg.PORT, log_level="info")
