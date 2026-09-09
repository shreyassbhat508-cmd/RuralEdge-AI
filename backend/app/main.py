from fastapi import FastAPI

app = FastAPI(
    title="RuralEdge API",
    description="Backend API for RuralEdge",
    version="1.0.0",
)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "RuralEdge Backend",
    }
