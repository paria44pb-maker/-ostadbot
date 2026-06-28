"""
🦅 OstadBot v8.0 | Main Entry Point
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# Import all parts
from part1 import *
from part2 import *
from part3 import *

# Run the application
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {APP_NAME} on port {PORT}")
    uvicorn.run("bot:app", host="0.0.0.0", port=PORT, log_level="info")
