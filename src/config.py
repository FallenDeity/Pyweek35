import math
import pathlib
import typing
from dataclasses import dataclass

from arcade import color

__all__: typing.Sequence[str] = (
    "GameConfig",
    "GoldenTanoi",
    "Danger",
    "Primary",
    "ArcadeGameStyles",
    "Paths",
)

RGB = tuple[int, int, int]


# Dimensions and title
@dataclass
class GameConfig:
    SCREEN_TITLE = "PyWeek35"
    SCREEN_HEIGHT = 600
    SCREEN_WIDTH = 800

    MUSIC_VOLUME = 0.5

    # Map size
    MAP_SIZE_X = 10
    MAP_SIZE_Y = 10

    # Camera
    CAMERA_MOVEMENT_SPEED = 5
    VIEWPORT_ANGLE = math.pi / 4
    INVERT_MOUSE = False


class BaseStyle:
    __slots__: tuple[str]

    def as_dict(self) -> dict[str, typing.Any]:
        return {attr: getattr(self, attr) for attr in self.__slots__}


@dataclass(slots=True)
class GoldenTanoi(BaseStyle):
    font_name: str = "Dilo World"
    font_color: RGB = (255, 207, 112)
    bg_color: RGB = (0, 140, 176)
    border_color: RGB = (0, 60, 75)


@dataclass(slots=True)
class Danger(BaseStyle):
    font_color = color.WHITE
    border_width: int = 2
    bg_color: RGB = (217, 4, 41)
    bg_color_pressed: RGB = (255, 166, 158)
    border_color_pressed: RGB = (255, 166, 158)


@dataclass(slots=True)
class Primary(BaseStyle):
    font_color = color.WHITE
    border_width: int = 2
    bg_color: RGB = (52, 152, 219)
    bg_color_pressed: RGB = (41, 128, 185)
    border_color_pressed: RGB = (41, 128, 185)


# Arcade styled dicts
@dataclass
class ArcadeGameStyles:
    golden_tanoi = (GoldenTanoi()).as_dict()
    danger = (Danger()).as_dict()
    primary = (Primary()).as_dict()


# Paths
@dataclass
class Paths:
    PATH = pathlib.Path(__file__).resolve().parent.parent
    ASSET_PATH = PATH / "assets"
    SRC_PATH = PATH / "src"
