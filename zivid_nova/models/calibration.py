from typing import Any, Optional

import zivid
import zivid.calibration
from pydantic import BaseModel, ConfigDict, Field

from zivid_nova.models.pose import Pose


class Calibration(BaseModel):
    """Calibration data structure with pydantic serialization"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    """Calibration ID"""

    serial_number: str
    """Serial number of the camera"""

    hand_eye_calibration: Optional[Pose]
    """Hand-Eye calibration pose"""

    poses: list[Any] = Field(exclude=True)
    """List of calibration poses"""

    detection_results: list[zivid.calibration.DetectionResult] = Field(exclude=True)
    """Results of the calibration board detection"""
