import typing as t


import arcade
import arcade.gui
from arcade.experimental.lights import LightLayer
from pyglet.math import Vec2  # type: ignore[reportMissingTypeStubs, reportUnknownVariableType]

from src.utils.constants import GameConfig
from src.utils.enums import Paths, Styles


class Menu(arcade.View):
    """
    Menu view.
    :param main_window: Main window in which the view is shown.
    """

    def __init__(self, main_window: arcade.Window) -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.v_box = None
        self.v_box_message = None
        self.manager = None
        self.background = arcade.load_texture((Paths.ASSETS / "titles" / "menu_background.jpg").as_posix())

    def on_show_view(self) -> None:
        """Called when the current is switched to this view."""
        self.setup()

    def setup(self) -> None:
        """Set up the game variables. Call to re-start the game."""
        self.v_box = arcade.gui.UIBoxLayout(space_between=10)
        self.v_box_message = arcade.gui.UIBoxLayout()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        play_button = arcade.gui.UIFlatButton(
            text="Play",
            width=200,
            style={
                "normal": arcade.gui.UIFlatButton.UIStyle(**Styles.GOLDEN_TANOI),
                "press": arcade.gui.UIFlatButton.UIStyle(),
                "hover": arcade.gui.UIFlatButton.UIStyle(),
                "disabled": arcade.gui.UIFlatButton.UIStyle(),
            }
        )
        play_button.on_click = self._on_click_play_button
        how_to_play_button = arcade.gui.UIFlatButton(
            text="How to Play",
            width=200,
            style={
                "normal": arcade.gui.UIFlatButton.UIStyle(**Styles.GOLDEN_TANOI),
                "press": arcade.gui.UIFlatButton.UIStyle(),
                "hover": arcade.gui.UIFlatButton.UIStyle(),
                "disabled": arcade.gui.UIFlatButton.UIStyle(),
            }
        )
        how_to_play_button.on_click = self._on_click_how_to_play_button
        exit_button = arcade.gui.UIFlatButton(
            text="Exit",
            width=200,
            style={
                "normal": arcade.gui.UIFlatButton.UIStyle(**Styles.GOLDEN_TANOI),
                "press": arcade.gui.UIFlatButton.UIStyle(),
                "hover": arcade.gui.UIFlatButton.UIStyle(),
                "disabled": arcade.gui.UIFlatButton.UIStyle(),
            }
        )
        exit_button.on_click = self._on_click_exit_button

        self.v_box.add(play_button)
        self.v_box.add(how_to_play_button)
        self.v_box.add(exit_button)
        self.manager.add(arcade.gui.UIAnchorLayout(children=(self.v_box,)))

    def _on_click_how_to_play_button(self, event: arcade.gui.UIOnClickEvent) -> None:
        message_box = arcade.gui.UIMessageBox(
            width=400,
            height=300,
            message_text="Welcome Good luck!",
        )
        message_box.on_action = self._how_to_play_callback
        v_box_message = t.cast(arcade.gui.UIBoxLayout, self.v_box_message)
        v_box_message.add(message_box)
        manager = t.cast(arcade.gui.UIManager, self.manager)
        manager.clear()
        manager.add(arcade.gui.UIAnchorLayout(children=(v_box_message,)))

    def _how_to_play_callback(self, event: arcade.gui.UIOnActionEvent) -> None:
        manager = t.cast(arcade.gui.UIManager, self.manager)
        v_box = t.cast(arcade.gui.UIBoxLayout, self.v_box)
        manager.clear()
        manager.add(arcade.gui.UIAnchorLayout(children=(v_box,)))

    def on_draw(self) -> None:
        """Called when this view should draw."""
        manager = t.cast(arcade.gui.UIManager, self.manager)
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0, GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT, self.background)
        manager.draw()

    def _on_click_play_button(self, event: arcade.gui.UIOnClickEvent) -> None:
        game = Game(self.main_window)
        game.setup()
        self.main_window.show_view(game)

    def _on_click_exit_button(self, event: arcade.gui.UIOnClickEvent) -> None:
        self.main_window.close()
        arcade.exit()

    def on_hide_view(self) -> None:
        manager = t.cast(arcade.gui.UIManager, self.manager)
        manager.disable()


class Game(arcade.View):
    """
    Main game logic goes here.
    :param main_window: Main window in which it showed.
    """

    def __init__(self, main_window: arcade.Window) -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.game_scene: t.Optional[arcade.Scene] = None
        self.camera_sprite: t.Optional[arcade.Sprite] = None
        self.physics_engine: t.Optional[arcade.PhysicsEnginePlatformer] = None
        self.camera: t.Optional[arcade.Camera] = None
        self.light_layer: t.Optional[LightLayer] = None
        self.screen_center_x: float = 0
        self.screen_center_y: float = 0
        self.manager: t.Optional[arcade.gui.UIManager] = None
        self.v_box: t.Optional[arcade.gui.UIBoxLayout] = None
        self.console_active: bool = False
        self.debugging_console: t.Optional[arcade.gui.UIInputText] = None
        self.debugging_console_tex_inp: t.Optional[arcade.Texture] = None
        self.debugging_console_tex_out: t.Optional[arcade.Texture] = None
        self.debugging_console_tex: t.Optional[arcade.gui.UIWidget] = None
        self.tic: int = 0

        self.player_list: t.Optional[arcade.SpriteList[arcade.Sprite]] = None
        self.wall_list: t.Optional[arcade.SpriteList[arcade.Sprite]] = None

    def on_show_view(self) -> None:
        """Called when the current is switched to this view."""
        #self.setup()

    def setup(self) -> None:
        """Set up the game here. Call this function to restart the game."""
        self.manager = arcade.gui.UIManager()
        self.v_box = arcade.gui.UIBoxLayout()
        self.debugging_console = arcade.gui.UIInputText(text=">", width=self.main_window.width, height=25)
        tex = arcade.texture.Texture.create_empty("tex creator", size=(GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        self.debugging_console_tex_inp = tex.create_filled(
            color=(100, 0, 0, 150),
            name="debug console in",
            size=(self.main_window.width, 25),
        )
        self.debugging_console_tex_out = tex.create_filled(
            color=(0, 100, 0, 150),
            name="debug console out",
            size=(self.main_window.width, 25),
        )
        self.debugging_console_tex = self.debugging_console.with_background(texture=self.debugging_console_tex_inp)
        self.v_box.add(self.debugging_console_tex)
        self.manager.add(arcade.gui.UIAnchorLayout(children=(self.v_box,), anchor_y="bottom"))
        self.manager.enable()
        self.game_scene = arcade.Scene()
        self.camera = arcade.Camera(anchor=(self.main_window.width, self.main_window.height,))
        self.camera_sprite = arcade.Sprite((Paths.ASSETS / "tiles" / "pnj.png").as_posix())
        self.camera_sprite.center_x = 0
        self.camera_sprite.center_y = 0
        self.game_scene.add_sprite("Camera", self.camera_sprite)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.camera_sprite, gravity_constant=0)
        self.light_layer = LightLayer(self.main_window.width, self.main_window.height)
        self.tic = 0

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        self.player_sprite = arcade.Sprite("C:\\Users\\XxHEROSOLDIERxX\\Desktop\\Pyweek35\\src\\assets\\tiles\\pnj.png")
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.player_list.append(self.player_sprite)

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear()
        camera = t.cast(arcade.Camera, self.camera)
        camera.use()
        if self.main_window.mouse_left_is_pressed:
            pass
        light_layer = t.cast(LightLayer, self.light_layer)
        game_scene = t.cast(arcade.Scene, self.game_scene)
        with light_layer:
            game_scene.draw()
        light_layer.draw(ambient_color=(255, 255, 255))
        manager = t.cast(arcade.gui.UIManager, self.manager)
        if self.console_active:
            manager.draw()

        assert self.player_list
        self.player_list.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Called whenever a key is pressed."""
        camera_sprite = t.cast(arcade.Sprite, self.camera_sprite)
        manager = t.cast(arcade.gui.UIManager, self.manager)
        debugging_console = t.cast(arcade.gui.UIInputText, self.debugging_console)
        debugging_console_tex = t.cast(arcade.gui.UIWidget, self.debugging_console_tex)
        debugging_console_tex_inp = t.cast(arcade.Texture, self.debugging_console_tex_inp)
        debugging_console_tex_out = t.cast(arcade.Texture, self.debugging_console_tex_out)
        v_box = t.cast(arcade.gui.UIBoxLayout, self.v_box)
        if symbol in (arcade.key.UP, arcade.key.W):
            camera_sprite.change_y = GameConfig.CAMERA_MOVEMENT_SPEED
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            camera_sprite.change_y = -GameConfig.CAMERA_MOVEMENT_SPEED
        elif symbol in (arcade.key.LEFT, arcade.key.A):
            camera_sprite.change_x = -GameConfig.CAMERA_MOVEMENT_SPEED
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            camera_sprite.change_x = GameConfig.CAMERA_MOVEMENT_SPEED
        elif symbol == arcade.key.F4:
            manager.enable()
            if self.console_active:
                manager.disable()
            self.console_active = not self.console_active
        elif symbol == arcade.key.ENTER:
            if not self.console_active:
                return
            if debugging_console.text[1:] in ("clear", "cls"):
                v_box.clear()
                self.debugging_console = arcade.gui.UIInputText(text=">", width=self.main_window.width, height=25)
                self.debugging_console_tex = self.debugging_console.with_background(texture=debugging_console_tex_inp)
                v_box.add(self.debugging_console_tex)
            else:
                out = arcade.gui.UILabel(
                    text=str(eval(f"{debugging_console.text[1:]}")),
                    width=self.main_window.width,
                    height=25,
                    text_color=(255, 255, 255),
                )
                out_tex = out.with_background(texture=debugging_console_tex_out)
                v_box.remove(debugging_console_tex)
                prev = arcade.gui.UILabel(
                    text=debugging_console.text,
                    width=self.main_window.width,
                    height=25,
                    text_color=(0, 0, 0),
                )
                prev_tex = prev.with_background(texture=debugging_console_tex_inp)
                v_box.add(prev_tex)
                v_box.add(out_tex)
                self.debugging_console = arcade.gui.UIInputText(text=">", width=self.main_window.width, height=25)
                self.debugging_console_tex = self.debugging_console.with_background(texture=debugging_console_tex_inp)
                v_box.add(self.debugging_console_tex)

    def on_key_release(self, key: int, _: t.Any) -> None:
        """Called when the user releases a key."""
        camera_sprite = t.cast(arcade.Sprite, self.camera_sprite)
        if key in (arcade.key.UP, arcade.key.W):
            camera_sprite.change_y = 0
        elif key in (arcade.key.DOWN, arcade.key.S):
            camera_sprite.change_y = 0
        elif key in (arcade.key.LEFT, arcade.key.A):
            camera_sprite.change_x = 0
        elif key in (arcade.key.RIGHT, arcade.key.D):
            camera_sprite.change_x = 0

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, _buttons: int, _modifiers: int) -> None:
        """Called when the mouse is dragged."""
        camera_sprite = t.cast(arcade.Sprite, self.camera_sprite)
        if GameConfig.INVERT_MOUSE:
            camera_sprite.center_x -= dx
            camera_sprite.center_y -= dy
        else:
            camera_sprite.center_x += dx
            camera_sprite.center_y += dy

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.main_window.mouse_x = x
        self.main_window.mouse_y = y

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.main_window.mouse_left_is_pressed = True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.main_window.mouse_left_is_pressed = False

    def center_camera_to_camera(self) -> None:
        """Centers camera to the camera sprite."""
        camera_sprite = t.cast(arcade.Sprite, self.camera_sprite)
        camera = t.cast(arcade.Camera, self.camera)
        self.screen_center_x = camera_sprite.center_x - (camera.viewport_width / 2)
        self.screen_center_y = camera_sprite.center_y - (camera.viewport_height / 2)
        camera_centered = Vec2(self.screen_center_x, self.screen_center_y)  # type: ignore[reportUnknownVariableType]
        camera.move_to(camera_centered)

    def on_update(self, delta_time: float) -> None:
        """Movement and game logic"""
        self.center_camera_to_camera()
        self.tic += 1


class WinLoseMenu(arcade.View):
    """
    Menu view.
    :param main_window: Main window in which the view is shown.
    """

    def __init__(self, main_window: arcade.Window, win_lose: str = "") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.v_box = None
        self.manager = None
        self.win_loose_message = win_lose
        self.background = arcade.load_texture((Paths.ASSETS / "titles" / "victory_background.jpg").as_posix())

    def on_show_view(self) -> None:
        """Called when the current is switched to this view."""
        self.setup()

    def setup(self) -> None:
        """Set up the game variables. Call to re-start the game."""
        self.v_box = arcade.gui.UIBoxLayout(space_between=10)
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        
        exit_button = arcade.gui.UIFlatButton(
            text="Exit",
            width=200,
            style={
                "normal": arcade.gui.UIFlatButton.UIStyle(**Styles.GOLDEN_TANOI),
                "press": arcade.gui.UIFlatButton.UIStyle(),
                "hover": arcade.gui.UIFlatButton.UIStyle(),
                "disabled": arcade.gui.UIFlatButton.UIStyle(),
            }
        )
        exit_button.on_click = self._on_click_exit_button
        restart_button = arcade.gui.UIFlatButton(
            text="Restart",
            width=200,
            style={
                "normal": arcade.gui.UIFlatButton.UIStyle(**Styles.GOLDEN_TANOI),
                "press": arcade.gui.UIFlatButton.UIStyle(),
                "hover": arcade.gui.UIFlatButton.UIStyle(),
                "disabled": arcade.gui.UIFlatButton.UIStyle(),
            }
        )
        restart_button.on_click = self._on_click_restart_button
        win_loose_button = arcade.gui.UIFlatButton(
            text=self.win_loose_message,
            width=200,
            style={
                "normal": arcade.gui.UIFlatButton.UIStyle(**Styles.GOLDEN_TANOI),
                "press": arcade.gui.UIFlatButton.UIStyle(),
                "hover": arcade.gui.UIFlatButton.UIStyle(),
                "disabled": arcade.gui.UIFlatButton.UIStyle(),
            }
        )
        
        self.v_box.add(win_loose_button)
        self.v_box.add(restart_button)
        self.v_box.add(exit_button)
        self.manager.add(arcade.gui.UIAnchorLayout(children=(self.v_box,)))

    def on_draw(self) -> None:
        """Called when this view should draw."""
        manager = t.cast(arcade.gui.UIManager, self.manager)
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0, GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT, self.background)
        manager.draw()

    def _on_click_restart_button(self, event: arcade.gui.UIOnClickEvent) -> None:
        game = Game(self.main_window)
        self.main_window.show_view(game)

    def _on_click_exit_button(self, event: arcade.gui.UIOnClickEvent) -> None:
        self.main_window.close()
        arcade.exit()

    def on_hide_view(self) -> None:
        manager = t.cast(arcade.gui.UIManager, self.manager)
        manager.disable()
