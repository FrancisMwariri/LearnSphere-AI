from fastapi import FastAPI

app = FastAPI(title="LearnSphere AI")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "application": "LearnSphere AI"}
