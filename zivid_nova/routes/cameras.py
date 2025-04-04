from io import BytesIO

import numpy as np
import point_cloud_utils as pcu
import rerun as rr
import zivid
import zivid.calibration
import zivid.firmware
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from PIL import Image

from zivid_nova import zivid_app
from zivid_nova.models.camera import Camera
from zivid_nova.models.capture_settings_preset import CaptureSettingsPreset
from zivid_nova.models.downsample_factor import DownsampleFactor
from zivid_nova.models.pose import Pose
from zivid_nova.utilities import is_rerun_enabled, rgba_to_rgb

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("")
async def get_cameras() -> list[Camera]:
    """Get all cameras"""

    return [Camera.from_zivid_camera(x) for x in zivid_app.get_cameras()]


@router.get("/{serial_number}")
async def get_camera(serial_number: str) -> Camera:
    """Get a camera by serial number"""

    return Camera.from_zivid_camera(zivid_app.get_connected_camera(serial_number))


@router.delete("/{serial_number}")
async def disconnect_camera(serial_number: str):
    """Disconnects a camera by serial number"""
    camera = zivid_app.get_camera(serial_number)
    if camera.state.connected:
        camera.disconnect()


@router.get("/{serial_number}/frame", responses={200: {"content": {"application/octet-stream": {}}}})
async def get_camera_frame(
    serial_number: str,
    down_sample_factor: DownsampleFactor = DownsampleFactor.NONE,
    preset: CaptureSettingsPreset = CaptureSettingsPreset.AUTO,
) -> FileResponse:
    """Get a frame from a camera in zdf format"""

    camera = zivid_app.get_connected_camera(serial_number)

    with zivid_app.get_camera_frame(camera, down_sample_factor, preset) as frame:
        filename = f"{camera.info.serial_number}.zdf"
        frame.save(filename)
        return FileResponse(filename, media_type="application/octet-stream", filename=filename)


@router.get("/{serial_number}/frame/pointcloud", responses={200: {"content": {"application/octet-stream": {}}}})
async def get_camera_frame_pointcloud(
    serial_number: str,
    down_sample_factor: DownsampleFactor = DownsampleFactor.NONE,
    preset: CaptureSettingsPreset = CaptureSettingsPreset.AUTO,
) -> FileResponse:
    """
    Get a point cloud from a camera in ply format.
    Point cloud will contain positions, colors and normals.
    Any points with NaN (position) values will be removed.
    """

    camera = zivid_app.get_connected_camera(serial_number)

    with zivid_app.get_camera_frame(camera, down_sample_factor, preset) as frame:
        filename = f"{camera.info.serial_number}.ply"

        colors = frame.point_cloud().copy_data("rgba")
        colors = colors.reshape((-1, 4))
        colors = colors[..., :] / 255
        positions = frame.point_cloud().copy_data("xyz").reshape(-1, 3)
        normals = frame.point_cloud().copy_data("normals").reshape(-1, 3)

        # Remove points with NaN values
        valid_indices = ~np.isnan(positions).any(axis=1)
        positions = positions[valid_indices]
        colors = colors[valid_indices]
        normals = normals[valid_indices]

        # saving the pointcloud via the frame.save("file.ply") method will ommit the normals
        pcu.save_mesh_vnc(filename, v=positions, n=normals, c=colors)

        frame.release()

        log_point_cloud(filename)
        return FileResponse(filename, media_type="application/octet-stream", filename=filename)


@router.get("/{serial_number}/frame/color-image", responses={200: {"content": {"image/png": {}}}})
async def get_camera_frame_color_image(
    serial_number: str,
    down_sample_factor: DownsampleFactor = DownsampleFactor.NONE,
    preset: CaptureSettingsPreset = CaptureSettingsPreset.AUTO,
) -> Response:
    """Get a color image from a camera"""

    camera = zivid_app.get_connected_camera(serial_number)

    with zivid_app.get_camera_frame(camera, down_sample_factor, preset) as frame:
        point_cloud = frame.point_cloud()
        rgb = rgba_to_rgb(point_cloud.copy_data("rgba"))
        buffer = BytesIO()
        image = Image.fromarray(rgb)
        image.save(buffer, "png")
        log_2d_image(buffer, "zivid/color_image")
        return Response(content=buffer.getvalue(), media_type="image/png")


@router.get("/{serial_number}/frame/depth-image", responses={200: {"content": {"image/png": {}}}})
async def get_camera_frame_depth_image(
    serial_number: str,
    down_sample_factor: DownsampleFactor = DownsampleFactor.NONE,
    preset: CaptureSettingsPreset = CaptureSettingsPreset.AUTO,
) -> Response:
    """Get a depth image from a camera"""

    camera = zivid_app.get_connected_camera(serial_number)

    with zivid_app.get_camera_frame(camera, down_sample_factor, preset) as frame:
        point_cloud = frame.point_cloud()
        depth = point_cloud.copy_data("z")
        depth_map_uint8 = ((depth - np.nanmin(depth)) / (np.nanmax(depth) - np.nanmin(depth)) * 255).astype(np.uint8)
        buffer = BytesIO()
        image = Image.fromarray(depth_map_uint8)
        image.save(buffer, "png")
        log_2d_image(buffer, "zivid/depth_image")
        return Response(content=buffer.getvalue(), media_type="image/png")


@router.get("/{serial_number}/frame/board-pose")
async def get_camera_frame_board_pose(serial_number: str) -> Pose:
    """Get the pose of the calibration board in the camera frame"""

    camera = zivid_app.get_connected_camera(serial_number)
    result = zivid.calibration.detect_calibration_board(camera)
    if not result.valid():
        # failed precondition
        raise HTTPException(status_code=412, detail="Calibration board not detected")
    pose = Pose.from_zivid_pose(result.pose())
    return pose


@router.get("/{serial_number}/frame2d", responses={200: {"content": {"image/png": {}}}})
async def get_camera_frame2d_color(serial_number: str) -> Response:
    """Get a color image from a camera"""

    camera = zivid_app.get_connected_camera(serial_number)

    with zivid_app.get_camera_frame2d(camera) as frame:
        buffer = BytesIO()
        image = Image.fromarray(frame.image_rgba().copy_data())
        image.save(buffer, "png")
        log_2d_image(buffer, "zivid/image")
        return Response(content=buffer.getvalue(), media_type="image/png")


@router.get("/{serial_number}/firmware/up-to-date")
async def get_camera_firmware_up_to_date(serial_number: str) -> bool:
    """Check if the camera firmware is up to date"""

    camera = zivid_app.get_camera(serial_number)
    if camera.state.connected:
        camera.disconnect()

    return zivid.firmware.is_up_to_date(camera)


@router.post("/{serial_number}/firmware/update")
async def update_camera_firmware(serial_number: str):
    """Update the camera firmware if necessary. Also performs downgrades."""

    camera = zivid_app.get_camera(serial_number)
    if camera.state.connected:
        camera.disconnect()

    zivid.firmware.update(camera)


def log_2d_image(image: BytesIO, name: str):
    if not is_rerun_enabled():
        return
    try:
        if image is not None:
            rr.log(name, rr.EncodedImage(media_type="image/png", contents=image.getvalue()))
    except Exception as e:
        print("Failed to log image to rerun", e)


def log_point_cloud(pcd_path: str):
    if not is_rerun_enabled():
        return
    try:
        rr.log_file_from_path(file_path=pcd_path, entity_path_prefix="zivid/pointcloud")
    except Exception as e:
        print("Failed to log pointcloud to rerun", e)
