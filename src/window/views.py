import typing

import arcade
import arcade.gui
from arcade.experimental.lights import LightLayer
from pyglet.math import Vec2  # type: ignore[reportMissingTypeStubs, reportUnknownVariableType]

from src.config import ArcadeGameStyles, GameConfig, Paths
from src.uitls import AssertAttrs


def assert_state(*args: typing.Any):
    """A decorator to check if the required attributes
    passed in as ``*args`` has been set on class.
    """

    def decorator(func: typing.Callable[..., typing.Any]):
        if all([bool(getattr(func.__class__, attr, None)) for attr in args]):
            return func

        raise RuntimeError("The Menu hasn't been setted up. " "It's required to call setup()")

    return decorator


class Menu(arcade.View):
    """
    Menu view.
    :param main_window: Main window in which the view is shown.
    """

    def __init__(self, main_window: arcade.Window):
        super().__init__(main_window)
        self.main_window = main_window
        self.v_box = None
        self.v_box_message = None
        self.manager = None
        self.background = arcade.load_texture(str(Paths.ASSET_PATH / "titles" / "menu_background.jpg"))

    def on_show_view(self) -> None:
        """Called when the current is switched to this view."""
        self.setup()

    def setup(self) -> None:
        """Set up the game variables. Call to re-start the game."""
        self.v_box = arcade.gui.UIBoxLayout(space_between=10)
        self.v_box_message = arcade.gui.UIBoxLayout()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        play_button = arcade.gui.UIFlatButton(text="Play", width=200, style=ArcadeGameStyles.golden_tanoi)
        play_button.on_click = self._on_click_play_button

        how_to_play_button = arcade.gui.UIFlatButton(text="How to Play", width=200, style=ArcadeGameStyles.golden_tanoi)
        how_to_play_button.on_click = self._on_click_how_to_play_button

        exit_button = arcade.gui.UIFlatButton(text="Exit", width=200, style=ArcadeGameStyles.golden_tanoi)
        exit_button.on_click = self._on_click_exit_button

        self.v_box.add(play_button)
        self.v_box.add(how_to_play_button)
        self.v_box.add(exit_button)

        self.manager.add(arcade.gui.UIAnchorWidget(child=self.v_box))

    @assert_state(AssertAttrs.ui_v_box_message, AssertAttrs.ui_manager)
    def _on_click_how_to_play_button(self, event: arcade.gui.UIOnClickEvent):
        message_box = arcade.gui.UIMessageBox(
            width=400, height=300, message_text="Welcome Good luck!", callback=self._how_to_play_callback
        )

        v_box_message = typing.cast(arcade.gui.UIBoxLayout, self.v_box_message)
        v_box_message.add(message_box)

        manager = typing.cast(arcade.gui.UIManager, self.manager)
        manager.clear()
        manager.add(arcade.gui.UIAnchorWidget(child=v_box_message))

    @assert_state(AssertAttrs.ui_manager, AssertAttrs.ui_v_box)
    def _how_to_play_callback(self, event: arcade.gui.UIOnClickEvent):
        manager = typing.cast(arcade.gui.UIManager, self.manager)
        v_box = typing.cast(arcade.gui.UIBoxLayout, self.v_box)

        manager.clear()
        manager.add(arcade.gui.UIAnchorWidget(child=v_box))

    @assert_state(AssertAttrs.ui_manager)
    def on_draw(self) -> None:
        """Called when this view should draw."""
        manager = typing.cast(arcade.gui.UIManager, self.manager)

        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0, GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT, self.background)
        manager.draw()

    def _on_click_play_button(self, event: arcade.gui.UIOnClickEvent) -> None:
        game = Game(self.main_window)
        self.main_window.show_view(game)

    def _on_click_exit_button(self, event: arcade.gui.UIOnClickEvent) -> None:
        self.main_window.close()
        arcade.exit()

    @assert_state(AssertAttrs.ui_manager)
    def on_hide_view(self):
        manager = typing.cast(arcade.gui.UIManager, self.manager)
        manager.disable()


class Game(arcade.View):
    """
    Main game logic goes here.
    :param main_window: Main window in which it showed.
    """

    def __init__(self, main_window: arcade.Window):
        super().__init__(main_window)
        self.main_window = main_window

        self.game_scene: typing.Optional[arcade.Scene] = None

        self.camera_sprite: typing.Optional[arcade.Sprite] = None
        self.physics_engine: typing.Optional[arcade.PhysicsEnginePlatformer] = None
        self.camera: typing.Optional[arcade.Camera] = None

        self.light_layer: typing.Optional[LightLayer] = None

        self.screen_center_x: float = 0
        self.screen_center_y: float = 0

        self.manager: typing.Optional[arcade.gui.UIManager] = None
        self.v_box: typing.Optional[arcade.gui.UIBoxLayout] = None
        self.console_active: bool = False

        self.debugging_console: typing.Optional[arcade.gui.UIInputText] = None
        self.debugging_console_tex_inp: typing.Optional[arcade.Texture] = None
        self.debugging_console_tex_out: typing.Optional[arcade.Texture] = None
        self.debugging_console_tex: typing.Optional[arcade.gui.UITexturePane] = None

        self.tic: int = 0

    def on_show_view(self):
        """Called when the current is switched to this view."""
        self.setup()

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.manager = arcade.gui.UIManager()
        self.v_box = arcade.gui.UIBoxLayout()
        self.debugging_console = arcade.gui.UIInputText(text=">", width=self.main_window.width, height=25)
        tex = arcade.texture.Texture("tex creator")
        self.debugging_console_tex_inp = tex.create_filled(
            color=(100, 0, 0, 150), name="debug console in", size=(self.main_window.width, 25)
        )
        self.debugging_console_tex_out = tex.create_filled(
            color=(0, 100, 0, 150), name="debug console out", size=(self.main_window.width, 25)
        )
        self.debugging_console_tex = self.debugging_console.with_background(self.debugging_console_tex_inp)
        self.v_box.add(self.debugging_console_tex)

        self.manager.add(arcade.gui.UIAnchorWidget(child=self.v_box, anchor_y="bottom"))
        self.manager.enable()

        self.game_scene = arcade.Scene()

        self.camera = arcade.Camera(self.main_window.width, self.main_window.height)

        self.camera_sprite = arcade.Sprite(str(Paths.ASSET_PATH / "tiles" / "pnj.png"))
        # this can be renamed to player sprite, if player sprite is decided to be made.
        self.camera_sprite = arcade.Sprite(str(Paths.ASSET_PATH / "tiles" / "pnj.png"))
        # self.camera_sprite.center_x = 400
        # self.camera_sprite.center_y = 300
        self.camera_sprite.center_x = 0
        self.camera_sprite.center_y = 0
        self.game_scene.add_sprite("Camera", self.camera_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.camera_sprite, gravity_constant=0)

        self.light_layer = LightLayer(self.main_window.width, self.main_window.height)

        self.tic = 0

    @assert_state(AssertAttrs.camera, AssertAttrs.light_layer, AssertAttrs.game_scene, AssertAttrs.ui_manager)
    def on_draw(self):
        """Render the screen."""
        self.clear()

        camera = typing.cast(arcade.Camera, self.camera)
        camera.use()
        # self.game_scene.draw()
        if self.main_window.mouse_left_is_pressed:
            pass

        light_layer = typing.cast(LightLayer, self.light_layer)
        game_scene = typing.cast(arcade.Scene, self.game_scene)
        with light_layer:
            game_scene.draw()
        light_layer.draw(ambient_color=(255, 255, 255))

        manager = typing.cast(arcade.gui.UIManager, self.manager)
        if self.console_active:
            manager.draw()

    @assert_state(
        AssertAttrs.camera_sprite,
        AssertAttrs.ui_manager,
        AssertAttrs.ui_v_box,
        AssertAttrs.debugging_console,
        AssertAttrs.debugging_console_tex,
        AssertAttrs.debugging_console_tex_inp,
        AssertAttrs.debugging_console_tex_out,
    )
    def on_key_press(self, key: int, _):
        """Called whenever a key is pressed."""
        # using change because if it is changed to player physics engine is required.
        camera_sprite = typing.cast(arcade.Sprite, self.camera_sprite)
        manager = typing.cast(arcade.gui.UIManager, self.manager)
        debugging_console = typing.cast(arcade.gui.UIInputText, self.debugging_console)
        debugging_console_tex = typing.cast(arcade.gui.UITexturePane, self.debugging_console_tex)
        debugging_console_tex_inp = typing.cast(arcade.Texture, self.debugging_console_tex_inp)
        debugging_console_tex_out = typing.cast(arcade.Texture, self.debugging_console_tex_out)
        v_box = typing.cast(arcade.gui.UIBoxLayout, self.v_box)

        if key in (arcade.key.UP, arcade.key.W):  # type: ignore[reportPrivateImportUsage]
            camera_sprite.change_y = GameConfig.CAMERA_MOVEMENT_SPEED
        elif key in (arcade.key.DOWN, arcade.key.S):  # type: ignore[reportPrivateImportUsage]
            camera_sprite.change_y = -GameConfig.CAMERA_MOVEMENT_SPEED
        elif key in (arcade.key.LEFT, arcade.key.A):  # type: ignore[reportPrivateImportUsage]
            camera_sprite.change_x = -GameConfig.CAMERA_MOVEMENT_SPEED
        elif key in (arcade.key.RIGHT, arcade.key.D):  # type: ignore[reportPrivateImportUsage]
            camera_sprite.change_x = GameConfig.CAMERA_MOVEMENT_SPEED
        elif key == arcade.key.F4:  # type: ignore[reportPrivateImportUsage]
            manager.enable()
            if self.console_active:
                manager.disable()
            self.console_active = not self.console_active
        elif key == arcade.key.ENTER:  # type: ignore[reportPrivateImportUsage]
            if not self.console_active:
                return
            if debugging_console.text[1:] in ("clear", "cls"):
                v_box.clear()
                self.debugging_console = arcade.gui.UIInputText(text=">", width=self.main_window.width, height=25)
                self.debugging_console_tex = self.debugging_console.with_background(debugging_console_tex_inp)
                v_box.add(self.debugging_console_tex)
            else:
                out = arcade.gui.UILabel(
                    text=str(eval(f"{debugging_console.text[1:]}")),
                    width=self.main_window.width,
                    height=25,
                    text_color=(255, 255, 255),
                )
                out_tex = out.with_background(debugging_console_tex_out)
                v_box.remove(debugging_console_tex)
                prev = arcade.gui.UILabel(
                    text=debugging_console.text, width=self.main_window.width, height=25, text_color=(0, 0, 0)
                )
                prev_tex = prev.with_background(debugging_console_tex_inp)
                v_box.add(prev_tex)
                v_box.add(out_tex)
                self.debugging_console = arcade.gui.UIInputText(text=">", width=self.main_window.width, height=25)
                self.debugging_console_tex = self.debugging_console.with_background(debugging_console_tex_inp)
                v_box.add(self.debugging_console_tex)

    @assert_state(AssertAttrs.camera_sprite)
    def on_key_release(self, key: int, _):
        """Called when the user releases a key."""
        camera_sprite = typing.cast(arcade.Sprite, self.camera_sprite)

        if key in (arcade.key.UP, arcade.key.W):  # type: ignore[reportPrivateImportUsage]
            camera_sprite.change_y = 0
        elif key in (arcade.key.DOWN, arcade.key.S):  # type: ignore[reportPrivateImportUsage]
            camera_sprite.change_y = 0
        elif key in (arcade.key.LEFT, arcade.key.A):  # type: ignore[reportPrivateImportUsage]
            camera_sprite.change_x = 0
        elif key in (arcade.key.RIGHT, arcade.key.D):  # type: ignore[reportPrivateImportUsage]
            camera_sprite.change_x = 0

    @assert_state(AssertAttrs.camera_sprite)
    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, _buttons: int, _modifiers: int):
        """Called when the mouse is dragged."""
        camera_sprite = typing.cast(arcade.Sprite, self.camera_sprite)

        if INVERT_MOUSE:
            camera_sprite.center_x -= dx
            camera_sprite.center_y -= dy
        else:
            camera_sprite.center_x += dx
            camera_sprite.center_y += dy

    def on_mouse_motion(self, x, y, dx, dy):
        self.main_window.mouse_x = x
        self.main_window.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.main_window.mouse_left_is_pressed = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.main_window.mouse_left_is_pressed = False

    @assert_state(AssertAttrs.camera_sprite, AssertAttrs.camera)
    def center_camera_to_camera(self):
        """Centers camera to the camera sprite."""
        camera_sprite = typing.cast(arcade.Sprite, self.camera_sprite)
        camera = typing.cast(arcade.Camera, self.camera)

        self.screen_center_x = camera_sprite.center_x - (camera.viewport_width / 2)
        self.screen_center_y = camera_sprite.center_y - (camera.viewport_height / 2)

        # pyglet.math doesn't have file stubs so meh
        camera_centered = Vec2(self.screen_center_x, self.screen_center_y)  # type: ignore[reportUnknownVariableType]
        camera.move_to(camera_centered)

    def on_update(self, delta_time):
        """Movement and game logic"""
        # self.physics_engine.update()
        # Position the camera
        self.center_camera_to_camera()

        self.tic += 1


class WinLooseMenu(arcade.View):
    """
    Menu view.
    :param main_window: Main window in which the view is shown.
    """

    def __init__(self, main_window: arcade.Window, win_loose=""):
        super().__init__(main_window)
        self.main_window = main_window
        self.v_box = None
        self.manager = None
        self.win_loose_message = win_loose
        self.background = arcade.load_texture(str(Paths.ASSET_PATH / "titles" / "victory_background.jpg"))

    def on_show_view(self) -> None:
        """Called when the current is switched to this view."""
        self.setup()

    def setup(self) -> None:
        """Set up the game variables. Call to re-start the game."""
        self.v_box = arcade.gui.UIBoxLayout(space_between=10)
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        win_loose_button = arcade.gui.UIFlatButton(
            text=self.win_loose_message, width=200, style=ArcadeGameStyles.golden_tanoi
        )

        restart_button = arcade.gui.UIFlatButton(text="Restart", width=200, style=ArcadeGameStyles.golden_tanoi)
        restart_button.on_click = self._on_click_restart_button

        exit_button = arcade.gui.UIFlatButton(text="Exit", width=200, style=ArcadeGameStyles.golden_tanoi)
        exit_button.on_click = self._on_click_exit_button

        self.v_box.add(win_loose_button)
        self.v_box.add(restart_button)
        self.v_box.add(exit_button)

        self.manager.add(arcade.gui.UIAnchorWidget(child=self.v_box))

    @assert_state(AssertAttrs.ui_manager)
    def on_draw(self) -> None:
        """Called when this view should draw."""
        manager = typing.cast(arcade.gui.UIManager, self.manager)

        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0, GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT, self.background)
        manager.draw()

    def _on_click_restart_button(self, event: arcade.gui.UIOnClickEvent) -> None:
        game = Game(self.main_window)
        self.main_window.show_view(game)

    def _on_click_exit_button(self, event: arcade.gui.UIOnClickEvent) -> None:
        self.main_window.close()
        arcade.exit()

    @assert_state(AssertAttrs.ui_manager)
    def on_hide_view(self):
        manager = typing.cast(arcade.gui.UIManager, self.manager)
        manager.disable()
