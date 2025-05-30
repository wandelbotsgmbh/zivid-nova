from typing import Any, Optional

import zivid
import zivid.calibration
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field

from zivid_nova.models.calibration_residual import CalibrationResidual
from zivid_nova.models.pose import Pose


class Calibration(BaseModel):
    """Calibration data structure with pydantic serialization"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    """Calibration ID"""

    serial_number: str
    """Serial number of the camera"""

    poses: list[Pose]
    """List of calibration poses"""

    detection_results: list[zivid.calibration.DetectionResult] = Field(exclude=True)
    """Results of the calibration board detection"""

    residuals: Optional[list[CalibrationResidual]]

    hand_eye_calibration: Optional[Pose]
    """Hand-Eye calibration pose"""

    def _assert_input_is_valid(self) -> None:
        if len(self.poses) != len(self.detection_results):
            raise ValueError(
                f"Number of poses ({len(self.poses)}) and detection results ({len(self.detection_results)}) do not match"
            )

    def add_pose(self, pose: Pose, detection_result: zivid.calibration.DetectionResult) -> None:
        """Add a pose and its corresponding detection result to the calibration"""
        logger.info(f"Add new pose {pose} with detection result {detection_result}")
        self.poses.append(pose)
        self.detection_results.append(detection_result)

    def remove_pose(self, index: int) -> None:
        """Remove a pose and its corresponding detection result from the calibration"""
        if index < 0 or index >= len(self.poses):
            raise IndexError("Index out of range")
        logger.info(f"Remove pose at index {index}")
        self.poses.pop(index)
        self.detection_results.pop(index)

    def recalibrate(self) -> None:
        """Recalculate the eye in hand calibration using the current input data"""
        self._assert_input_is_valid()

        if len(self.poses) < 2:
            logger.info("Not enough calibration poses to compute hand-eye calibration.")
            return

        hand_eye_input = []

        for calibration_pose, detection_result in zip(self.poses, self.detection_results):
            hand_eye_input.append(zivid.calibration.HandEyeInput(calibration_pose.to_zivid_pose(), detection_result))

        hand_eye_output = zivid.calibration.calibrate_eye_in_hand(hand_eye_input)

        logger.info("Residuals: \n")
        self.residuals = [CalibrationResidual.from_zivid(residual) for residual in hand_eye_output.residuals()]
        for residual in self.residuals:
            logger.info(f"Translation: {residual.translation:.6f}   Rotation: {residual.rotation:.6f}")

        self.hand_eye_calibration = Pose.from_matrix(hand_eye_output.transform())
        logger.info(f"Calibration computed on {len(hand_eye_input)} points.")
        logger.info(f"Calibration pose: {self.hand_eye_calibration}")
