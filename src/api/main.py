from typing import Any
from fastapi import FastAPI
from src.settings.app_settigns import AppSettings
from src.api.routers.query import router as query_router


app: FastAPI = FastAPI(
    debug=AppSettings().debug,
    title=AppSettings().app_name,
    version=AppSettings().version,
    openapi_url="/api/openapi.json",
    docs_url="/api",
    redoc_url=None,
)


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "version": AppSettings().version}


app.include_router(query_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=AppSettings().fastapi_host,
        port=AppSettings().fastapi_port,
    )
