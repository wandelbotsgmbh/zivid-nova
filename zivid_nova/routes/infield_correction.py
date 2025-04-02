from fastapi import APIRouter, HTTPException
from zivid_nova import zivid_app
import zivid
from loguru import logger
import uuid

# TODO https://support.zivid.com/en/latest/academy/camera/infield-correction/infield-correction-cli-tool.html
router = APIRouter(prefix="/infield-correction", tags=["infield-correction"])

correction_states = {}


class Infield_Correction_State:
    def __init__(self, serial_number: str, correction_id: str):
        self.camera_id = serial_number
        self.correction_id = correction_id
        self.dataset = []


@router.get("")
async def read(serial_number: str) -> str:
    """the read function will return the last time an infield correction was written to the camera."""
    camera = zivid_app.get_connected_camera(serial_number)
    if zivid.experimental.calibration.has_camera_correction(camera):
        timestamp = zivid.experimental.calibration.camera_correction_timestamp(camera)
        return {timestamp.strftime(r'%Y-%m-%d %H:%M:%S')}
    else:
        raise HTTPException(status_code=404, detail="No infield correction found on camera.")

@router.get("/verification")
async def verify(serial_number: str):
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
    camera = zivid_app.get_connected_camera(serial_number)
    state = Infield_Correction_State(serial_number=camera.serial_number(), correction_id=str(uuid.uuid4()))
    correction_states[state.correction_id] = state
    return state.correction_id


@router.post("/{correction_id}")
async def add_correction_dataset(correction_id: str):
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
    logger.info(f"Collected {len(state.dataset)} dataset for infield correction.")


@router.put("/{correction_id}")
async def write_correction_dataset(correction_id: str):
    """
    Calculates the correction based on the current dataset for the run.
    """
    state = get_correction_state(correction_id)
    camera = zivid_app.get_connected_camera(state.serial_number)
    correction = zivid.experimental.calibration.compute_camera_correction(state.dataset)
    accuracy_estimate = correction.accuracy_estimate()
    logger.info(
        "This correction can be expected to yield a dimension accuracy error of",
        f"{accuracy_estimate.dimension_accuracy() * 100:.3f}% or better in the range of z=[{accuracy_estimate.z_min():.3f}, {accuracy_estimate.z_max():.3f}] across the full FOV.",
        "Accuracy close to where the correction data was collected is likely better.",
    )
    logger.info("Writing correction to camera...")
    zivid.experimental.calibration.write_camera_correction(camera, correction)


@router.delete("/{correction_id}")
async def delete_correction_dataset(correction_id: str) -> str:
    """ """
    return "hello world"


def get_correction_state(correction_id: str) -> Infield_Correction_State:
    if correction_id in correction_states:
        return correction_states[correction_id]
    raise HTTPException(status_code=404, detail="Correction ID not found")


def verify_infield_input(infield_input):
    """
    Verify if the infield input is valid for infield correction.
    """
    if not infield_input.valid():
        raise HTTPException(
            status_code=404,
            detail=f"Capture not valid for infield correction! Feedback: {infield_input.status_description()}",
        )


def verify_detection_result(detection_result):
    if not detection_result.valid():
        raise HTTPException(
            status_code=404, detail=f"Calibration board not detected! Feedback: {detection_result.status_description()}"
        )
