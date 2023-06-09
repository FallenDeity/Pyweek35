import arcade


class Window(arcade.Window):
    """Main application class."""

    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)  # type: ignore
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_left_is_pressed = False
        arcade.set_background_color(arcade.color.ANTI_FLASH_WHITE)