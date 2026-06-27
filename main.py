from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    print("APP IS RUNNING")
    return {"status": "ok"}
