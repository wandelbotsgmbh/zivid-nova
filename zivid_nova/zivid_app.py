from datetime import timedelta
from pathlib import Path

import zivid
import zivid.application
import zivid.calibration
import zivid.capture_assistant
from loguru import logger

from zivid_nova.models.capture_settings_preset import CaptureSettingsPreset
from zivid_nova.models.downsample_factor import DownsampleFactor

try:
    app = zivid.Application()
except RuntimeError:
    app = None
    logger.warning("Could not initialize zivid application. Probably no graphics card available.")

camera_cache: dict[str, zivid.Camera] = {}

def _update_camera_cache():
    """Update the camera cache"""
    global camera_cache

    # Keep connected camera references because new references are not connected
    camera_cache = { kv[0]: kv[1] for kv in camera_cache.items() if kv[1].state.connected }

    for camera in app.cameras():
        if not camera.info.serial_number in camera_cache:
            camera_cache[camera.info.serial_number] = camera

def get_cameras() -> list[zivid.Camera]:
    """Get a list of all cameras."""

    _update_camera_cache()
    return list(camera_cache.values())

def get_connected_camera(serial_number: str) -> zivid.Camera:
    """Get a camera by serial number. Makes sure the camera is connected."""

    # Check if camera is in cache. If not, update cache and try again
    if not serial_number in camera_cache:
        _update_camera_cache()
        if not serial_number in camera_cache:
            raise ValueError(f"Camera with serial number {serial_number} not found")
    
    camera = camera_cache[serial_number]
    
    # Cameras can be disconnected during operation. Reconnect if needed.
    # If it fails remove it from the cache and raise an error
    try:
        if not camera.state.connected:
            camera.connect()
    except:
        camera_cache.pop(serial_number)
        raise ValueError(f"Camera with serial number {serial_number} not found")

    return camera

def _get_settings(camera: zivid.Camera, preset: CaptureSettingsPreset) -> zivid.Settings:
    """Get settings for a camera and a preset. Loads settings from file or suggests settings if preset is AUTO"""

    if preset is CaptureSettingsPreset.AUTO:
        suggest_settings_parameters = zivid.capture_assistant.SuggestSettingsParameters(
            max_capture_time=timedelta(milliseconds=800),
            ambient_light_frequency=zivid.capture_assistant.SuggestSettingsParameters.AmbientLightFrequency.none,
        )
        return zivid.capture_assistant.suggest_settings(camera, suggest_settings_parameters)

    settings_file = str(Path(__file__).parent / "resources" / preset.to_filename())
    return zivid.Settings.load(settings_file)


def get_camera_frame(
    camera: zivid.Camera, down_sample_factor: DownsampleFactor, preset: CaptureSettingsPreset
) -> zivid.Frame:
    """Get a frame from a camera. Downsample the point cloud if requested"""
    settings = _get_settings(camera, preset)
    frame = camera.capture(settings)

    if isinstance(frame, zivid.Frame):
        if down_sample_factor is not DownsampleFactor.NONE:
            frame.point_cloud().downsample(down_sample_factor.to_zivid())
        return frame

    raise ValueError("Unhandled frame type")


def _get_settings2d() -> zivid.Settings2D:
    """Get settings2d for a camera"""

    settings_file = str(Path(__file__).parent / "resources/Zivid2_Settings_Zivid_Two_M70_Default2D.yml")
    return zivid.Settings2D.load(settings_file)


def get_camera_frame2d(camera: zivid.Camera) -> zivid.Frame2D:
    """Get a frame2d from a camera"""
    settings = _get_settings2d()
    frame = camera.capture(settings)

    if isinstance(frame, zivid.Frame2D):
        return frame

    raise ValueError("Unhandled frame type")
