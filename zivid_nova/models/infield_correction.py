from typing import List

import pydantic
import zivid


class CameraVerification(pydantic.BaseModel):
    """CameraVerification"""

    local_dimension_trueness: float
    """Local dimension trueness error of the camera"""

    position: List[float]
    """Position of the camera"""

    @classmethod
    def from_zivid_camera_verification(
        cls, camera_verification: zivid.experimental.calibration.CameraVerification
    ) -> "CameraVerification":
        """Create a CameraVerification instance from a zivid.experimental.calibration.CameraVerification instance"""

        return cls(
            local_dimension_trueness=camera_verification.local_dimension_trueness(),
            position=camera_verification.position(),
        )


class AddCorrectionOffsetResp(pydantic.BaseModel):
    """AddCorrectionOffsetResp data structure with pydantic serialization"""

    dimension_accuracy: float
    """estimated dimension accuracy obtained if the correction is applied"""

    dataset_size: int
    """size of the dataset of the correction run"""

    z_min: float
    """
    Get the range of validity of the accuracy estimate (lower end).
    Minimum z-value of working volume in millimeters.
    """

    z_max: float
    """
    Get the range of validity of the accuracy estimate (upper end).
    Maximum z-value of working volume in millimeters.
    """
