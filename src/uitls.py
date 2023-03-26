from enum import StrEnum


class AssertAttrs(StrEnum):
    ui_manager = "manager"

    ui_v_box = "v_box"
    ui_v_box_message = "v_box_message"

    camera = "camera"
    camera_sprite = "camera_sprite"

    light_layer = "light_layer"
    game_scene = "game_scene"

    debugging_console = "debugging_console"
    debugging_console_tex = "debugging_console_tex"
    debugging_console_tex_inp = "debugging_console_tex_inp"
    debugging_console_tex_out = "debugging_console_tex_out"
