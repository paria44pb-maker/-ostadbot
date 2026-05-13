from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
import execution.trade_router as trade_router

app = FastAPI(
    title="WhaleMind AI",
    version="1.0.0",
    description="AI Trading System with Nobitex Integration"
)

# =========================================================
# Home Route
# =========================================================

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "WhaleMind AI is running",
        "mode": trade_router.MODE
    }

# =========================================================
# Health Check
# =========================================================

@app.get("/health")
def health():
    return {
        "server": "ok",
        "trading_mode": trade_router.MODE
    }

# =========================================================
# Trade Request Model
# =========================================================

class TradeRequest(BaseModel):

    mode: Optional[Literal["paper", "live"]] = Field(
        default=None,
        description="paper or live"
    )

    side: Literal["buy", "sell"]

    symbol: str = Field(
        default="btc-usdt",
        description="Trading symbol"
    )

    amount: float = Field(
        ...,
        gt=0,
        description="Trade amount"
    )

    price: Optional[float] = Field(
        default=None,
        description="Optional limit price"
    )

    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


# =========================================================
# Execute Trade Endpoint
# =========================================================

@app.post("/trade")
def execute_trade(req: TradeRequest):

    try:

        # تغییر حالت سیستم
        if req.mode:
            trade_router.MODE = req.mode

        result = trade_router.route_trade(
            side=req.side,
            symbol=req.symbol,
            amount=req.amount,
            price=req.price,
            stop_loss=req.stop_loss,
            take_profit=req.take_profit
        )

        return {
            "success": True,
            "mode": trade_router.MODE,
            "trade": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================================
# Quick Test Trade
# =========================================================

@app.get("/test-trade")
def test_trade():

    try:

        result = trade_router.route_trade(
            side="buy",
            symbol="btc-usdt",
            amount=0.001,
            price=60000
        )

        return {
            "success": True,
            "message": "Test trade executed",
            "result": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================================
# Get Current Mode
# =========================================================

@app.get("/mode")
def get_mode():

    return {
        "current_mode": trade_router.MODE
    }

# =========================================================
# Change Mode
# =========================================================

@app.post("/mode/{mode}")
def change_mode(mode: str):

    if mode not in ["paper", "live"]:

        raise HTTPException(
            status_code=400,
            detail="Mode must be 'paper' or 'live'"
        )

    trade_router.MODE = mode

    return {
        "success": True,
        "new_mode": trade_router.MODE
    }

# =========================================================
# View Paper Positions
# =========================================================

@app.get("/paper-positions")
def get_paper_positions():

    return {
        "count": len(trade_router.paper_positions),
        "positions": trade_router.paper_positions
    }

# =========================================================
# Clear Paper Positions
# =========================================================

@app.delete("/paper-positions")
def clear_paper_positions():

    trade_router.paper_positions.clear()

    return {
        "success": True,
        "message": "Paper positions cleared"
    }
