import zivid
from decouple import config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from zivid_nova import routes

BASE_PATH = config("BASE_PATH", default="", cast=str)

version = "dev"

# Stoplight Elements version for offline UI
STOPLIGHT_VERSION = "9.0.8"

app = FastAPI(
    title="Zivid Nova Plugin",
    version=version,
    description="Zivid Nova API",
    contact={
        "name": "Wandelbots GmbH",
        "email": "engineering-platform@wandelbots.com",
        "url": "https://www.wandelbots.com",
    },
    docs_url="/docs",
    dependencies=[],
    root_path=BASE_PATH,
    swagger_ui_parameters={"tryItOutEnabled": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.calibrations.router)
app.include_router(routes.cameras.router)
app.include_router(routes.infield_correction.router)
app.include_router(routes.projector.router)

# Mount static files for offline Stoplight Elements
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    # One could serve a nice UI here as well. For simplicity and discoverability, we show the Stoplight UI
    return f"""
    <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <title>Elements in HTML</title>
            <!-- Embed elements Elements via Web Component -->
            <script src="{BASE_PATH}/static/stoplight-{STOPLIGHT_VERSION}/web-components.min.js"></script>
            <link rel="stylesheet" href="{BASE_PATH}/static/stoplight-{STOPLIGHT_VERSION}/styles.min.css">
          </head>
          <body>

            <elements-api
              apiDescriptionUrl="{BASE_PATH}/openapi.json"
              router="hash"
              layout="sidebar"
              tryItCredentialsPolicy="same-origin"
            />

          </body>
    </html>
    """


@app.get("/version")
async def get_version():
    return {
        "zivid_nova": version,
        "zivid_sdk": zivid.__version__,
        "stoplight_elements": STOPLIGHT_VERSION,
    }


@app.get("/healthz")
async def healthz():
    """Health check endpoint that reports warm-up status."""
    from zivid_nova import zivid_app

    return {
        "warmed": getattr(zivid_app, "_warmed", False),
        "warmup_enabled": getattr(zivid_app, "_ENABLE_WARMUP", False),
    }


@app.get("/app_icon.png", summary="Services the app icon for the homescreen")
async def get_app_icon():
    try:
        return FileResponse(path="static/app_icon.png", media_type="image/png")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Icon not found") from e
