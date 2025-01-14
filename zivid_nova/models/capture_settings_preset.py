from enum import Enum, unique


@unique
class CaptureSettingsPreset(str, Enum):
    """Different capture settings presets"""

    AUTO = "auto"
    DIFFUSE = "diffuse"
    SEMISPECULAR = "semispecular"
    SPECULAR = "specular"

    def to_filename(self) -> str:
        """Convert to filename"""
        mapping = {
            CaptureSettingsPreset.AUTO: "",
            CaptureSettingsPreset.DIFFUSE: "Zivid2_Settings_Zivid_Two_M70_ManufacturingDiffuse.yml",
            CaptureSettingsPreset.SEMISPECULAR: "Zivid2_Settings_Zivid_Two_M70_ManufacturingSemiSpecular.yml",
            CaptureSettingsPreset.SPECULAR: "Zivid2_Settings_Zivid_Two_M70_ManufacturingSpecular.yml",
        }
        return mapping[self]
