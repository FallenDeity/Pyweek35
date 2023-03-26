import math
import typing as t

# constans.py

__all__: tuple[str] = ("GameConfig",)


@t.final
class GameConfig:
    SCREEN_TITLE: t.Final[str] = "PyWeek35"
    SCREEN_HEIGHT: t.Final[int] = 600
    SCREEN_WIDTH: t.Final[int] = 800
    MUSIC_VOLUME: t.Final[float] = 0.5
    MAP_SIZE_X: t.Final[int] = 10
    MAP_SIZE_Y: t.Final[int] = 10
    CAMERA_MOVEMENT_SPEED: t.Final[int] = 5
    VIEWPORT_ANGLE: t.Final[float] = math.pi / 4
    INVERT_MOUSE: t.Final[bool] = False
