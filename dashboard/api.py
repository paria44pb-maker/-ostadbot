from fastapi import FastAPI

app = FastAPI()

@app.get("/stats")
def stats():
    return {
        "users": 1200,
        "vip": 300,
        "revenue": "$4500"
    }
