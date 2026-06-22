from fastapi import FastAPI
from aqf_backend.routers import repository, aqf, query, usability

app = FastAPI(title="AQF Demo Backend", version="0.1.0")

app.include_router(repository.router, prefix="/repository", tags=["repository"])
app.include_router(aqf.router, prefix="/aqf", tags=["aqf"])
app.include_router(query.router, prefix="/query", tags=["query"])
app.include_router(usability.router, prefix="/usability", tags=["usability"])


@app.get("/health")
def health():
    return {"status": "ok"}
