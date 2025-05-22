import uuid

import zivid
import zivid.calibration
from fastapi import APIRouter
from loguru import logger

from zivid_nova.models.calibration import Calibration
from zivid_nova.models.pose import Pose
from zivid_nova.zivid_app import get_connected_camera, zivid_lock

router = APIRouter(prefix="/calibrations", tags=["calibrations"])

calibrations: dict[str, Calibration] = {}


@router.get("")
@zivid_lock
def get_calibrations() -> list[Calibration]:
    """Get all calibrations"""

    return list(calibrations.values())


@router.delete("")
@zivid_lock
def delete_calibrations():
    """Delete all calibrations"""

    calibrations.clear()


@router.post("")
@zivid_lock
def start_calibration(serial_number: str) -> Calibration:
    """Start a new calibration"""

    camera = get_connected_camera(serial_number)
    calibration = Calibration(
        id=str(uuid.uuid4()),
        serial_number=camera.info.serial_number,
        poses=[],
        detection_results=[],
        residuals=None,
        hand_eye_calibration=None,
    )
    calibrations[calibration.id] = calibration
    return calibration


@router.get("/{calibration_id}")
@zivid_lock
def get_calibration(calibration_id: str) -> Calibration:
    """Get a calibration by ID"""

    return calibrations[calibration_id]


@router.post("/{calibration_id}/poses")
@zivid_lock
def add_calibration_pose(calibration_id: str, pose: Pose) -> Calibration:
    """Add a calibration pose to a calibration"""

    calibration = calibrations[calibration_id]
    camera = get_connected_camera(calibration.serial_number)
    result = zivid.calibration.detect_calibration_board(camera)

    if not result.valid():
        logger.info("Calibration board not detected.")
        return calibration

    calibration.add_pose(pose, result)
    calibration.recalibrate()

    return calibration


@router.delete("/{calibration_id}/poses/{pose_id}")
@zivid_lock
def delete_calibration_pose(calibration_id: str, pose_id: int) -> Calibration:
    """Delete a calibration pose from a calibration"""

    calibration = calibrations[calibration_id]
    calibration.remove_pose(pose_id)
    calibration.recalibrate()
    return calibration


@router.delete("/{calibration_id}")
@zivid_lock
def delete_calibration(calibration_id: str):
    """Delete a calibration by ID"""

    del calibrations[calibration_id]
