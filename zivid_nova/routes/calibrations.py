import uuid

import zivid
import zivid.calibration
from fastapi import APIRouter
from loguru import logger

from zivid_nova.models.calibration import Calibration
from zivid_nova.models.pose import Pose
from zivid_nova.zivid_app import get_connected_camera

router = APIRouter(prefix="/calibrations", tags=["calibrations"])

calibrations: dict[str, Calibration] = {}


@router.get("")
async def get_calibrations() -> list[Calibration]:
    """Get all calibrations"""

    return list(calibrations.values())


@router.delete("")
async def delete_calibrations():
    """Delete all calibrations"""

    calibrations.clear()


@router.post("")
async def start_calibration(serial_number: str) -> Calibration:
    """Start a new calibration"""

    camera = get_connected_camera(serial_number)
    calibration = Calibration(
        id=str(uuid.uuid4()),
        serial_number=camera.info.serial_number,
        poses=[],
        detection_results=[],
        hand_eye_calibration=None,
    )
    calibrations[calibration.id] = calibration
    return calibration


@router.get("/{calibration_id}")
async def get_calibration(calibration_id: str) -> Calibration:
    """Get a calibration by ID"""

    return calibrations[calibration_id]


@router.post("/{calibration_id}")
async def add_calibration_pose(calibration_id: str, pose: Pose) -> Calibration:
    """Add a calibration pose to a calibration"""

    calibration = calibrations[calibration_id]
    camera = get_connected_camera(calibration.serial_number)
    result = zivid.calibration.detect_calibration_board(camera)

    if not result.valid():
        logger.info("Calibration board not detected.")
        return calibration

    calibration.poses.append(pose)
    calibration.detection_results.append(result)

    hand_eye_input = []
    for calibration_pose, detection_result in zip(calibration.poses, calibration.detection_results):
        hand_eye_input.append(zivid.calibration.HandEyeInput(calibration_pose.to_zivid_pose(), detection_result))

    if len(hand_eye_input) < 2:
        return calibration

    hand_eye_output = zivid.calibration.calibrate_eye_in_hand(hand_eye_input)

    residuals = hand_eye_output.residuals()
    logger.info("Residuals: \n")
    for residual in residuals:
        logger.info(f"Translation: {residual.translation():.6f}   Rotation: {residual.rotation():.6f}")

    calibration_pose = Pose.from_matrix(hand_eye_output.transform())
    logger.info(f"Calibration computed on {len(hand_eye_input)} points.")
    logger.info(f"Calibration pose: {calibration_pose}")

    calibration.hand_eye_calibration = calibration_pose

    return calibration


@router.delete("/{calibration_id}")
async def delete_calibration(calibration_id: str):
    """Delete a calibration by ID"""

    del calibrations[calibration_id]
