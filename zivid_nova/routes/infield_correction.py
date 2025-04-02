import uuid
from typing import List

import zivid
import zivid.calibration
import zivid.experimental.calibration
from fastapi import APIRouter, HTTPException
from loguru import logger
from zivid.calibration import DetectionResult
from zivid.experimental.calibration import InfieldCorrectionInput

from zivid_nova import zivid_app
from zivid_nova.models.infield_correction import AddCorrectionOffsetResp, CameraVerification

router = APIRouter(prefix="/infield-correction", tags=["infield-correction"])

correction_states = {}


class Infield_Correction_State:
    def __init__(self, serial_number: str, correction_id: str):
        self.serial_number = serial_number
        self.correction_id = correction_id
        self.dataset = []


@router.get("")
async def read(serial_number: str) -> str:
    """the read function will return the last time an infield correction was written to the camera."""
    camera = zivid_app.get_connected_camera(serial_number)
    if zivid.experimental.calibration.has_camera_correction(camera):
        timestamp = zivid.experimental.calibration.camera_correction_timestamp(camera)
        return timestamp.strftime(r"%Y-%m-%d %H:%M:%S")
    else:
        raise HTTPException(status_code=404, detail="No infield correction found on camera.")


@router.get("/verification")
async def verify(serial_number: str) -> CameraVerification:
    """
    This function uses a single capture to determine the local dimension trueness error
    of the point cloud where the Zivid calibration board is placed.
    """
    camera = zivid_app.get_connected_camera(serial_number)

    detection_result = zivid.calibration.detect_calibration_board(camera)
    verify_detection_result(detection_result)

    infield_input = zivid.experimental.calibration.InfieldCorrectionInput(detection_result)
    verify_infield_input(infield_input)

    camera_verification = zivid.experimental.calibration.verify_camera(infield_input)

    logger.info(
        f"Estimated dimension trueness error at measured position: {camera_verification.local_dimension_trueness() * 100:.3f}%"
    )

    pos = camera_verification.position()
    logger.info(f"Position: {pos}")

    return CameraVerification.from_zivid_camera_verification(camera_verification)


@router.delete("")
async def reset(serial_number: str):
    """
    Using reset will remove any infield correction that has been applied in previous correct instances.
    It is not required to do a reset before doing a new infield correction.
    """
    camera = zivid_app.get_connected_camera(serial_number)
    zivid.experimental.calibration.reset_camera_correction(camera)


@router.get("/correction")
async def list_correction(serial_number: str) -> List[str]:
    """
    List all correction run IDs for the given serial number.
    """
    zivid_app.get_connected_camera(serial_number)
    correction_ids = []
    for correction_id in correction_states:
        if correction_states[correction_id].serial_number == serial_number:
            correction_ids.append(correction_id)
    return correction_ids


@router.post("/correction")
async def start_correction(serial_number: str) -> str:
    """
    Will start a new correction run, by collection a dataset under the returned ID.
    """
    zivid_app.get_connected_camera(serial_number)
    state = Infield_Correction_State(serial_number=serial_number, correction_id=str(uuid.uuid4()))
    correction_states[state.correction_id] = state
    return state.correction_id


@router.post("/correction/{correction_id}")
async def add_correction_dataset(correction_id: str) -> AddCorrectionOffsetResp:
    """
    Add a new dataset to the correction run.
    """
    state = get_correction_state(correction_id)
    camera = zivid_app.get_connected_camera(state.serial_number)

    detection_result = zivid.calibration.detect_calibration_board(camera)
    verify_detection_result(detection_result)

    infield_input = zivid.experimental.calibration.InfieldCorrectionInput(detection_result)
    verify_infield_input(infield_input)

    state.dataset.append(infield_input)
    logger.info(f"Collected {len(state.dataset)} datasets for infield correction.")

    correction = zivid.experimental.calibration.compute_camera_correction(state.dataset)
    accuracy_estimate = correction.accuracy_estimate()

    result = AddCorrectionOffsetResp(
        dimension_accuracy=accuracy_estimate.dimension_accuracy(),
        dataset_size=len(state.dataset),
        z_min=accuracy_estimate.z_min(),
        z_max=accuracy_estimate.z_max(),
    )

    logger.info(f"Current estimated result {result}")
    return result


@router.put("/correction/{correction_id}")
async def write_correction_dataset(correction_id: str):
    """
    Calculates the correction based on the current dataset for the run. Clears the previous dataset.
    """
    state = get_correction_state(correction_id)
    camera = zivid_app.get_connected_camera(state.serial_number)
    correction = zivid.experimental.calibration.compute_camera_correction(state.dataset)
    accuracy_estimate = correction.accuracy_estimate()
    logger.info(
        f"This correction can be expected to yield a dimension accuracy error of {accuracy_estimate.dimension_accuracy() * 100:.3f}% or better in the range of z=[{accuracy_estimate.z_min():.3f}, {accuracy_estimate.z_max():.3f}] across the full FOV. Accuracy close to where the correction data was collected is likely better.",
    )
    logger.info("Writing correction to camera...")
    zivid.experimental.calibration.write_camera_correction(camera, correction)
    del correction_states[correction_id]


@router.delete("/correction/{correction_id}")
async def delete_correction_dataset(correction_id: str):
    """ """
    if correction_id in correction_states:
        del correction_states[correction_id]


def get_correction_state(correction_id: str) -> Infield_Correction_State:
    if correction_id in correction_states:
        return correction_states[correction_id]
    raise HTTPException(status_code=404, detail="Correction ID not found")


def verify_infield_input(infield_input: InfieldCorrectionInput):
    """
    Verify if the infield input is valid for infield correction.
    """
    if not infield_input.valid():
        raise HTTPException(
            status_code=404,
            detail=f"Capture not valid for infield correction! Feedback: {infield_input.status_description()}",
        )


def verify_detection_result(detection_result: DetectionResult):
    if not detection_result.valid():
        raise HTTPException(
            status_code=404, detail=f"Calibration board not detected! Feedback: {detection_result.status_description()}"
        )
