import enum
import pathlib
import typing as t

from .models import RGB, Style

__all__: tuple[str, ...] = (
    "BaseEnum",
    "Styles",
    "Paths",
)


class BaseEnum(enum.Enum):
    def __get__(self, instance: t.Any, owner: t.Any) -> t.Any:
        return self.value


class Styles(BaseEnum):
    GOLDEN_TANOI = Style(
        font_name="Dilo World",
        font_color=RGB(255, 207, 112),
        bg_color=RGB(0, 140, 176),
        border_color=RGB(0, 60, 75),
    )
    DANGER = Style(
        font_color=RGB(255, 255, 255),
        border_width=2,
        bg_color=RGB(217, 4, 41),
        bg_color_pressed=RGB(255, 166, 158),
        border_color_pressed=RGB(255, 166, 158),
    )
    PRIMARY = Style(
        font_color=RGB(255, 255, 255),
        border_width=2,
        bg_color=RGB(0, 123, 255),
        bg_color_pressed=RGB(0, 110, 230),
        border_color_pressed=RGB(0, 110, 230),
    )

    def __get__(self, instance: t.Any, owner: t.Any) -> t.Any:
        return {k: v for k, v in self.value.to_dict().items() if v is not None}


class Paths(BaseEnum):
    BASE = pathlib.Path(__file__).resolve().parent.parent
    ASSETS = BASE / "assets"  # type: ignore
    SRC = BASE / "src"  # type: ignore
