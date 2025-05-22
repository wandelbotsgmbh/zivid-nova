from pydantic import BaseModel
from zivid.calibration import HandEyeResidual

class CalibrationResidual(BaseModel):
    """Calibration residual data structure with pydantic serialization"""

    translation: float
    """Translation residual in mm"""

    rotation: float
    """Rotation residual in degrees"""

    
    @classmethod
    def from_zivid(cls, residual: HandEyeResidual) -> "CalibrationResidual":
        """Create a CalibrationResidual instance from a zivid HandEyeResidual instance"""

        return cls(
            translation=residual.translation(),
            rotation=residual.rotation(),
        )