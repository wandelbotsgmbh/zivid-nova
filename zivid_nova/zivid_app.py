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


def find_camera(serial_number: str) -> zivid.Camera:
    """Find a camera by serial number"""

    for camera in app.cameras():
        if camera.info.serial_number == serial_number:
            return camera

    raise ValueError(f"Camera with serial number {serial_number} not found")


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

    if not camera.state.connected:
        camera.connect()

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

    if not camera.state.connected:
        camera.connect()

    settings = _get_settings2d()
    frame = camera.capture(settings)

    if isinstance(frame, zivid.Frame2D):
        return frame

    raise ValueError("Unhandled frame type")


def get_calibration_board(camera: zivid.Camera) -> zivid.calibration.DetectionResult:
    """Detect calibration board in the camera view"""

    if not camera.state.connected:
        camera.connect()
    return zivid.calibration.detect_calibration_board(camera)
