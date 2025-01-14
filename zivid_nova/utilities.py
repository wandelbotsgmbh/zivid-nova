import socket

import numpy as np
from decouple import config

# needs to be provided in format "hostname:port" or "ip:port"
RERUN_ADDR = config("RERUN_ADDR", default="", cast=str)


def rgba_to_rgb(rgba: np.ndarray) -> np.ndarray:
    """Converts an RGBA image to an RGB image by removing the last element of each pixel."""
    return rgba[..., :-1]


def is_rerun_enabled() -> bool:
    """
    Checks if rerun.io should be enabled.
    """
    return RERUN_ADDR != ""


def rerun_connection_str() -> str:
    """
    Returns the connection string for rerun.io.

    Since rerun.io requires an IP address, this function will resolve the hostname to an IP address
    and returns the sting in the format 'ip:port'.
    """

    if not is_rerun_enabled():
        raise ValueError("RERUN_ADDR is not set")

    if ":" not in RERUN_ADDR:
        raise ValueError("RERUN_ADDR must be in format 'hostname:port' or 'ip:port'")

    split = RERUN_ADDR.split(":")

    if len(split) != 2:
        raise ValueError("RERUN_ADDR must be in format 'hostname:port' or 'ip:port'")

    ip_addr_list = socket.gethostbyname_ex(split[0])[2]
    if len(ip_addr_list) == 0:
        raise ValueError(f"Invalid hostname for rerun {split[0]}")

    port = RERUN_ADDR.split(":")[1]
    return f"{ip_addr_list[0]}:{port}"
