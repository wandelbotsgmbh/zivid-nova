import json
import os

import rerun as rr
import uvicorn
from loguru import logger

from zivid_nova.app import app
from zivid_nova.utilities import is_rerun_enabled, rerun_connection_str

_BANNER = r"""
███████╗██╗██╗   ██╗██╗██████╗       ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ 
╚══███╔╝██║██║   ██║██║██╔══██╗      ████╗  ██║██╔═══██╗██║   ██║██╔══██╗
  ███╔╝ ██║██║   ██║██║██║  ██║█████╗██╔██╗ ██║██║   ██║██║   ██║███████║
 ███╔╝  ██║╚██╗ ██╔╝██║██║  ██║╚════╝██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║
███████╗██║ ╚████╔╝ ██║██████╔╝      ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║
╚══════╝╚═╝  ╚═══╝  ╚═╝╚═════╝       ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝
"""


def main(host: str = "0.0.0.0", port: int = 8080):
    log_level = os.getenv("LOG_LEVEL", "info")
    port = int(os.getenv("PORT", port))
    logger.info(_BANNER)
    logger.info("Starting Service...")
    if is_rerun_enabled():
        connection = rerun_connection_str()
        logger.info(f"Connecting rerun with: {connection}")
        rr.init(application_id="zivid_nova", recording_id="6d2ba503-cc8e-4097-8e3c-35a5f7de56a6")
        rr.connect_tcp(connection)

    uvicorn.run(
        app, host=host, port=port, reload=False, log_level=log_level, proxy_headers=True, forwarded_allow_ips="*"
    )


def generate_schema():
    with open("openapi.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(app.openapi()))
