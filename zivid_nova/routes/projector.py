from typing import Dict

import zivid
from fastapi import APIRouter
from loguru import logger
from zivid.projection import ProjectedImage, projector_resolution, show_image_bgra

from zivid_nova import zivid_app
from zivid_nova.zivid_app import zivid_lock

router = APIRouter(prefix="/projectors", tags=["projectors"])

handles: Dict[str, ProjectedImage] = {}


@router.post("/{serial_number}")
@zivid_lock
def project_test_image(serial_number: str):
    """
    Starts projection of a test image for calibration board adjustment.
    Stops the previous projection.
    Selects the appropriate image based on the projector resolution.
    """
    if serial_number in handles:
        logger.info(f"Stopping existing projector handle for {serial_number}...")
        handles[serial_number].stop()

    camera = zivid_app.get_connected_camera(serial_number)
    proj_resolution = projector_resolution(camera)
    target_height, target_width = proj_resolution
    logger.info(f"Detected projector resolution: {target_width}x{target_height}")

    # Decide which image to load based on resolution
    if (target_width, target_height) == (1280, 720):
        image_path = "static/image2.png"
    elif (target_width, target_height) == (1000, 720):
        image_path = "static/image2+.png"
    else:
        logger.error(f"Unsupported projector resolution: {target_width}x{target_height}")
        raise ValueError(f"Unsupported projector resolution: {target_width}x{target_height}")

    logger.info(f"Loading image: {image_path}")

    # Load image
    image = zivid.Image.load(image_path, "rgba")

    # Start projection
    handles[serial_number] = show_image_bgra(camera, image.copy_data())


@router.delete("/{serial_number}")
@zivid_lock
def delete_projection(serial_number: str):
    """
    Stops the projection for the given camera.
    """
    if serial_number not in handles:
        return
    logger.info(f"Stopping projector handle for {serial_number}...")
    handles[serial_number].stop()
