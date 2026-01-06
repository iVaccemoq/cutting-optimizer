# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.algorithm import optimize_cut


app = FastAPI()

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для диплома допустимо
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/optimize")
def optimize(data: dict):
    """
    data = {
        "stocks": [
            {
                "length": 6000,
                "quantity": 3,
                "name": "Труба 6м",
                "priority": 1,
                "material": "steel"
            }
        ],
        "cuts": [
            {
                "length": 1500,
                "quantity": 4,
                "name": "Отрезок A",
                "material": "steel"
            }
        ]
    }
    """
    return optimize_cut(
        stocks=data["stocks"],
        cuts=data["cuts"],
        settings=data.get("settings")
    )


