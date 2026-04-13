"""Cross Web documentation website."""

import sys
from pathlib import Path

from cross_docs import CrossDocs
from cross_inertia import configure_inertia
from cross_inertia.fastapi.experimental import inertia_lifespan
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

configure_inertia(
    vite_entry="app.tsx",
    vite_command=[sys.executable, "-m", "pybun", "run", "dev"],
    template_dir="templates",
    manifest_path="static/build/.vite/manifest.json",
    ssr_enabled=True,
    ssr_command=[sys.executable, "-m", "pybun", "frontend/dist/ssr/ssr.js"],
)

app = FastAPI(
    title="Cross Web",
    docs_url="/__fastapi/docs",
    redoc_url="/__fastapi/redoc",
    swagger_ui_oauth2_redirect_url="/__fastapi/oauth2-redirect",
    lifespan=inertia_lifespan,
)

app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)

docs = CrossDocs()
docs.mount(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
