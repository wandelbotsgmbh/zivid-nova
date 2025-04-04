
from fastapi import APIRouter
import zivid
from loguru import logger
import numpy as np
from typing import Dict

from zivid_nova import zivid_app
from zivid.projection import ProjectedImage, show_image_bgra, projector_resolution


router = APIRouter(prefix="/projectors", tags=["projectors"])

handles: Dict[str, ProjectedImage] = {}

@router.post("/{serial_number}")
async def project_test_image(serial_number: str):
    """
    Starts projection of a testimage for calibration board adjustment. 
    Stops the previous projection.
    """
    if serial_number in handles:
        logger.info(f"stopping projector handle for {serial_number}...")
        handles[serial_number].stop()

    camera = zivid_app.get_connected_camera(serial_number)
    resolution = projector_resolution(camera)
    logger.info(f"Projector resolution: {resolution}")

    # TODO support other resolutions as well
    if resolution != (720, 1280):
        logger.warning(f"Projector resolution is not 720x1280, but {resolution}")
    
    image = zivid.Image.load("static/image.png", "rgba")
    handles[serial_number] = show_image_bgra(camera, image.copy_data())


@router.delete("/{serial_number}")
async def delete_projection(serial_number: str):
    """
    Stops the projection for the given camera.
    """
    if serial_number not in handles:
        return
    logger.info(f"stopping projector handle for {serial_number}...")
    handles[serial_number].stop()

