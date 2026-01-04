# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.algorithm import optimize_cut

app = FastAPI()

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для диплома можно, в проде ограничивают
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
        "sheet": {"width": 1000, "height": 500},
        "parts": [
            {"width": 200, "height": 100},
            {"width": 300, "height": 200}
        ]
    }
    """
    return optimize_cut(data["sheet"], data["parts"])
