import json
import zipfile
from io import BytesIO
from pathlib import Path

import numpy as np
import OpenEXR
from PIL import Image

from zivid_nova.models.camera_intrinsics import CameraIntrinsics
from zivid_nova.nova_camera_frame import NovaCameraFrame, nova_camera_frame_to_zip, write_nova_camera_frame

_HEIGHT = 4
_WIDTH = 5


def _read_exr(path: Path) -> np.ndarray:
    channels = OpenEXR.File(str(path), separate_channels=True).channels()
    planes = [channels[name].pixels for name in ("R", "G", "B") if name in channels]
    return planes[0] if len(planes) == 1 else np.stack(planes, axis=-1)


def _nova_camera_frame() -> NovaCameraFrame:
    rng = np.random.default_rng(0)
    points = rng.uniform(-500.0, 500.0, size=(_HEIGHT, _WIDTH, 3)).astype(np.float32)
    points[0, 0] = np.nan
    normals = rng.normal(size=(_HEIGHT, _WIDTH, 3)).astype(np.float32)
    normals /= np.linalg.norm(normals, axis=-1, keepdims=True)
    normals[0, 0] = np.nan
    return NovaCameraFrame(
        color=rng.integers(0, 256, size=(_HEIGHT, _WIDTH, 3), dtype=np.uint8),
        depth=points[..., 2].copy(),
        normals=normals,
        points=points,
        snr=rng.uniform(0.0, 100.0, size=(_HEIGHT, _WIDTH)).astype(np.float32),
        intrinsics=CameraIntrinsics(fx=1.0, fy=2.0, cx=3.0, cy=4.0, k1=5.0, k2=6.0, k3=7.0, p1=8.0, p2=9.0),
    )


def test_write_nova_camera_frame_round_trips_every_pass(tmp_path: Path):
    # Arrange
    frame = _nova_camera_frame()

    # Act
    write_nova_camera_frame(frame, tmp_path)

    # Assert
    np.testing.assert_array_equal(np.array(Image.open(tmp_path / "color.png")), frame.color)
    np.testing.assert_array_equal(_read_exr(tmp_path / "depth.exr"), frame.depth)
    np.testing.assert_array_equal(_read_exr(tmp_path / "normal.exr"), frame.normals)
    np.testing.assert_array_equal(_read_exr(tmp_path / "pointcloud.exr"), frame.points)
    np.testing.assert_array_equal(_read_exr(tmp_path / "snr.exr"), frame.snr)
    assert json.loads((tmp_path / "intrinsics.json").read_text(encoding="utf-8")) == frame.intrinsics.model_dump()


def test_write_nova_camera_frame_stores_vectors_as_rgb_and_scalars_as_r_channel(tmp_path: Path):
    # Arrange
    frame = _nova_camera_frame()

    # Act
    write_nova_camera_frame(frame, tmp_path)

    # Assert
    for filename, expected_channels in [
        ("depth.exr", {"R"}),
        ("normal.exr", {"R", "G", "B"}),
        ("pointcloud.exr", {"R", "G", "B"}),
        ("snr.exr", {"R"}),
    ]:
        channels = OpenEXR.File(str(tmp_path / filename), separate_channels=True).channels()
        assert set(channels) == expected_channels
        assert all(channel.pixels.dtype == np.float32 for channel in channels.values())


def test_nova_camera_frame_to_zip_contains_one_file_per_pass():
    # Arrange
    frame = _nova_camera_frame()

    # Act
    with zipfile.ZipFile(BytesIO(nova_camera_frame_to_zip(frame))) as archive:
        filenames = sorted(archive.namelist())

    # Assert
    assert filenames == [
        "color.png",
        "depth.exr",
        "intrinsics.json",
        "normal.exr",
        "pointcloud.exr",
        "snr.exr",
    ]
