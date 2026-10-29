import pydantic
import zivid


class CameraIntrinsics(pydantic.BaseModel):
    """Pinhole camera matrix and Brown-Conrady distortion in the OpenCV convention, in pixels"""

    fx: float
    fy: float
    cx: float
    cy: float
    k1: float
    k2: float
    k3: float
    p1: float
    p2: float

    @classmethod
    def from_zivid_intrinsics(cls, intrinsics: zivid.CameraIntrinsics) -> "CameraIntrinsics":
        """Create a CameraIntrinsics instance from a zivid.CameraIntrinsics instance"""

        camera_matrix = intrinsics.camera_matrix
        distortion = intrinsics.distortion
        return cls(
            fx=camera_matrix.fx,
            fy=camera_matrix.fy,
            cx=camera_matrix.cx,
            cy=camera_matrix.cy,
            k1=distortion.k1,
            k2=distortion.k2,
            k3=distortion.k3,
            p1=distortion.p1,
            p2=distortion.p2,
        )
