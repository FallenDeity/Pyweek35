import typing as t
from abc import ABC

import attrs

__all__: tuple[str, ...] = (
    "Style",
    "RGB",
    "BaseModel",
)


@attrs.define(kw_only=True, frozen=True, slots=True)
class BaseModel(ABC):
    def to_dict(self) -> dict[str, t.Any]:
        return attrs.asdict(self)


@attrs.define(frozen=True, slots=True)
class RGB(BaseModel):
    red: int
    green: int
    blue: int


@attrs.define(kw_only=True, frozen=True, slots=True)
class Style(BaseModel):
    font_name: t.Optional[str] = None
    font_color: t.Optional[RGB] = None
    bg: t.Optional[RGB] = None
    border: t.Optional[RGB] = None
    border_width: t.Optional[int] = None
    bg_color_pressed: t.Optional[RGB] = None
    border_color_pressed: t.Optional[RGB] = None

    def to_dict(self) -> dict[str, t.Any]:
        return {
            key: tuple(value.values()) if isinstance(value, dict) else value
            for key, value in attrs.asdict(self).items()
        }
