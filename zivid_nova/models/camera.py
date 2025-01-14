import pydantic
import zivid


class Camera(pydantic.BaseModel):
    """Camera data structure with pydantic serialization"""

    serial_number: str
    """Serial number of the camera"""

    model: str
    """Model of the camera"""

    firmware_version: str
    """Firmware version of the camera"""

    @classmethod
    def from_zivid_camera(cls, camera: zivid.Camera) -> "Camera":
        """Create a Camera instance from a zivid.Camera instance"""

        return cls(
            serial_number=camera.info.serial_number,
            model=camera.info.model,
            firmware_version=camera.info.firmware_version,
        )
