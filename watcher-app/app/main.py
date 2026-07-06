from fastapi import FastAPI

app = FastAPI(title="AIOps Incident Watcher")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Watcher service is alive"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
