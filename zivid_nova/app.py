import zivid
import zivid.application
from decouple import config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from zivid_nova import routes

BASE_PATH = config("BASE_PATH", default="", cast=str)

version = "dev"

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


@app.get("/")
async def root():
    # One could serve a nice UI here as well. For simplicity, we just redirect to the swagger docs page.
    return RedirectResponse(url=BASE_PATH + "/docs")


@app.get("/version")
async def get_version():
    return {"zivid_nova": version, "zivid_sdk": zivid.__version__}


@app.get("/app_icon.png", summary="Services the app icon for the homescreen")
async def get_app_icon():
    try:
        return FileResponse(path="static/app_icon.png", media_type="image/png")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Icon not found") from e
