import numpy as np
import zivid
import zivid.calibration
from pydantic import BaseModel
from scipy.spatial.transform import Rotation as R


class Pose(BaseModel):
    """Pose with position and orientation. Orientation is represented as a rotation vector"""

    position: tuple[float, float, float]
    """Position of the pose"""

    orientation: tuple[float, float, float]
    """Orientation of the pose as a rotation vector"""

    @classmethod
    def from_zivid_pose(cls, pose: zivid.calibration.Pose) -> "Pose":
        return cls.from_matrix(pose.to_matrix())

    @classmethod
    def from_matrix(cls, matrix: np.ndarray) -> "Pose":
        position = matrix[:3, 3].tolist()
        rot_vec = R.from_matrix(matrix[:3, :3]).as_rotvec().tolist()
        return cls(position=position, orientation=rot_vec)

    def to_matrix(self) -> np.ndarray:
        rotation = R.from_rotvec(self.orientation)
        matrix = np.eye(4)
        matrix[:3, :3] = rotation.as_matrix()
        matrix[:3, 3] = self.position
        return matrix

    def to_zivid_pose(self) -> zivid.calibration.Pose:
        return zivid.calibration.Pose(self.to_matrix())
