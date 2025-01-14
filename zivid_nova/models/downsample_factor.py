from enum import IntEnum, unique

import zivid
import zivid.point_cloud


@unique
class DownsampleFactor(IntEnum):
    """Downsample factor for pointclouds"""

    NONE = 1
    BY2X2 = 2
    BY3X3 = 3
    BY4X4 = 4

    def to_zivid(self) -> zivid.point_cloud.PointCloud.Downsampling:
        """Convert to Zivid SDK enum"""
        mapping = {
            DownsampleFactor.NONE: None,
            DownsampleFactor.BY2X2: zivid.point_cloud.PointCloud.Downsampling.by2x2,
            DownsampleFactor.BY3X3: zivid.point_cloud.PointCloud.Downsampling.by3x3,
            DownsampleFactor.BY4X4: zivid.point_cloud.PointCloud.Downsampling.by4x4,
        }
        return mapping[self]
