from fastapi import FastAPI

app = FastAPI()

@app.get("/metrics")
def metrics():
    return {
        "users": 5300,
        "active_vip": 1200,
        "signals_today": 45,
        "accuracy": "78%"
    }
