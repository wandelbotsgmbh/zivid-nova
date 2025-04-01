

from fastapi import APIRouter
from zivid_nova import zivid_app
import zivid
from loguru import logger

# TODO https://support.zivid.com/en/latest/academy/camera/infield-correction/infield-correction-cli-tool.html
router = APIRouter(prefix="/infield-correction", tags=["infield-correction"])

correction_states = {}

class Infield_Correction_State:

    def __init__(self, correction_id: str):
        self.correction_id = correction_id
        self.dataset = []

@router.get("")
async def read(serial_number: str) -> str:
    """the read function will return the last time an infield correction was written to the camera."""
    return "hello world"

@router.get("/verification")
async def verify(serial_number: str):
    """
    This function uses a single capture to determine the local dimension trueness error
    of the point cloud where the Zivid calibration board is placed.
    """
    camera = zivid_app.get_connected_camera(serial_number)
    detection_result = zivid.calibration.detect_calibration_board(camera)
    if not detection_result.valid():
        raise RuntimeError(
            f"Calibration board not detected! Feedback: {detection_result.status_description()}"
        )

    infield_input = zivid.experimental.calibration.InfieldCorrectionInput(detection_result)
    if not infield_input.valid():
        raise RuntimeError(
            f"Capture not valid for infield verification! Feedback: {infield_input.status_description()}"
        )
    
    camera_verification = zivid.experimental.calibration.verify_camera(infield_input)
    logger.info(
        f"Estimated dimension trueness error at measured position: {camera_verification.local_dimension_trueness() * 100:.3f}%"
    )

    return camera_verification

@router.delete("")
async def reset(serial_number: str):
    """
    Using reset will remove any infield correction that has been applied in previous correct instances. 
    It is not required to do a reset before doing a new infield correction.
    """
    pass

@router.post("")
async def start_correction(serial_number: str) -> str:
    """
    Will start a new correction run, by collection a dataset under the returned ID.
    """
    # todo debatable 
    correction_states.clear()
    return "hello world"

@router.post("/{correction_id}")
async def add_correction_dataset(correction_id: str) -> str:
    """
    """
    return "hello world"

@router.put("/{correction_id}")
async def write_correction_dataset(correction_id: str) -> str:
    """
    """
    return "hello world"

@router.delete("/{correction_id}")
async def delete_correction_dataset(correction_id: str) -> str:
    """
    """
    return "hello world"
