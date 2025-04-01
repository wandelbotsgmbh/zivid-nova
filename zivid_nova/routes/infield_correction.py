

from fastapi import APIRouter


router = APIRouter(prefix="/infield-correction", tags=["infield-correction"])

@router.get("")
async def read(serial_number: str) -> str:
    """the read function will return the last time an infield correction was written to the camera."""
    return "hello world"

@router.delete("")
async def reset(serial_number: str) -> str:
    """
    Using reset will remove any infield correction that has been applied in previous correct instances. 
    It is not required to do a reset before doing a new infield correction.
    """
    return "hello world"

@router.post("")
async def start_correction(serial_number: str) -> str:
    """
    Will start a new correction run, by collection a dataset under the returned ID.
    """
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
