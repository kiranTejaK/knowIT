from fastapi import FastAPI

app = FastAPI(title="KnowIT", description="Modular RAG Platform")

@app.get("/")
def read_root():
    return {
        "application": "KnowIT",
        "status": "running"
    }
