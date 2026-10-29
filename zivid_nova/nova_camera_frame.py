"""
Per-pixel data of a 3D frame in the Nova capture layout.

All passes share the pixel grid of the point cloud. Lengths are millimetres in the Zivid camera
frame, which follows the OpenCV convention: +X right, +Y down, +Z along the viewing direction.
Pixels without a valid measurement hold NaN in the depth, normal and point cloud passes.
"""

import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import OpenEXR
from PIL import Image

from zivid_nova.models.camera_intrinsics import CameraIntrinsics

COLOR_FILENAME = "color.png"
DEPTH_FILENAME = "depth.exr"
NORMAL_FILENAME = "normal.exr"
POINTCLOUD_FILENAME = "pointcloud.exr"
SNR_FILENAME = "snr.exr"
INTRINSICS_FILENAME = "intrinsics.json"


@dataclass(frozen=True)
class NovaCameraFrame:
    """Per-pixel data of a 3D frame"""

    color: np.ndarray
    """(H, W, 3) uint8 sRGB color"""

    depth: np.ndarray
    """(H, W) distance along +Z"""

    normals: np.ndarray
    """(H, W, 3) unit surface normals"""

    points: np.ndarray
    """(H, W, 3) X, Y and Z of the surface point seen by each pixel"""

    snr: np.ndarray
    """(H, W) signal-to-noise ratio of each point"""

    intrinsics: CameraIntrinsics
    """Intrinsics matching the resolution of the passes"""


def write_nova_camera_frame(frame: NovaCameraFrame, directory: Path) -> None:
    """
    Write the passes of the frame into `directory`.

    Color is an 8-bit PNG. The other passes are float32 EXRs: 3-vectors are stored in the R, G and B
    channels, scalars in the R channel. The intrinsics are a JSON file.
    """

    Image.fromarray(frame.color).save(directory / COLOR_FILENAME)
    _write_exr(directory / DEPTH_FILENAME, frame.depth)
    _write_exr(directory / NORMAL_FILENAME, frame.normals)
    _write_exr(directory / POINTCLOUD_FILENAME, frame.points)
    _write_exr(directory / SNR_FILENAME, frame.snr)
    (directory / INTRINSICS_FILENAME).write_text(frame.intrinsics.model_dump_json(indent=2), encoding="utf-8")


def nova_camera_frame_to_zip(frame: NovaCameraFrame) -> bytes:
    """Write the frame into a zip archive with one file per pass, see `write_nova_camera_frame`"""

    buffer = BytesIO()
    with TemporaryDirectory() as directory:
        write_nova_camera_frame(frame, Path(directory))
        # PNG and EXR are compressed already
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
            for path in sorted(Path(directory).iterdir()):
                archive.write(path, arcname=path.name)
    return buffer.getvalue()


def _write_exr(path: Path, pixels: np.ndarray) -> None:
    channel_name = "RGB" if pixels.ndim == 3 else "R"
    header = {"compression": OpenEXR.ZIP_COMPRESSION, "type": OpenEXR.scanlineimage}
    # The OpenEXR binding reads the raw buffer and ignores strides.
    channels = {channel_name: np.ascontiguousarray(pixels, dtype=np.float32)}
    with OpenEXR.File(header, channels) as exr_file:
        exr_file.write(str(path))
