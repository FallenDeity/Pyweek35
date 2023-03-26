import datetime
import random
import time

import arcade
import arcade.gui
from arcade.experimental.lights import LightLayer

from config import (ASSET_PATH, CAMERA_MOVEMENT_SPEED, INVERT_MOUSE,
                    MAP_SIZE_X, MAP_SIZE_Y, SCREEN_HEIGHT,
                    SCREEN_WIDTH, STYLE_GOLDEN_TANOI)


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
        self.background = arcade.load_texture(str(ASSET_PATH / "titles" / "menu_background.jpg"))

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
            text="Play", width=200, style=STYLE_GOLDEN_TANOI)
        play_button.on_click = self._on_click_play_button

        how_to_play_button = arcade.gui.UIFlatButton(
            text="How to Play", width=200, style=STYLE_GOLDEN_TANOI)
        how_to_play_button.on_click = self._on_click_how_to_play_button

        exit_button = arcade.gui.UIFlatButton(
            text="Exit", width=200, style=STYLE_GOLDEN_TANOI)
        exit_button.on_click = self._on_click_exit_button

        self.v_box.add(play_button)
        self.v_box.add(how_to_play_button)
        self.v_box.add(exit_button)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                child=self.v_box
            )
        )

    def _on_click_how_to_play_button(self, _: arcade.gui.UIOnClickEvent):
        message_box = arcade.gui.UIMessageBox(
            width=400,
            height=300,
            message_text="Welcome Good luck!",
            callback=self._how_to_play_callback)

        self.v_box_message.add(message_box)
        self.manager.clear()
        self.manager.add(arcade.gui.UIAnchorWidget(child=self.v_box_message))

    def _how_to_play_callback(self, _: arcade.gui.UIOnClickEvent):
        self.manager.clear()
        self.manager.add(arcade.gui.UIAnchorWidget(child=self.v_box))

    def on_draw(self) -> None:
        """Called when this view should draw."""
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        self.manager.draw()

    def _on_click_play_button(self, _: arcade.gui.UIOnClickEvent) -> None:
        game = Game(self.main_window)
        self.main_window.show_view(game)

    def _on_click_exit_button(self, _: arcade.gui.UIOnClickEvent) -> None:
        self.main_window.close()
        arcade.exit()

    def on_hide_view(self):
        self.manager.disable()


class Game(arcade.View):
    """
    Main game logic goes here.
    :param main_window: Main window in which it showed.
    """

    def __init__(self, main_window: arcade.Window):
        super().__init__(main_window)
        self.main_window = main_window

        self.game_scene: arcade.Scene = None

        self.camera_sprite = None
        self.physics_engine = None
        self.camera: arcade.Camera = None

        self.light_layer = None

        self.screen_center_x = 0
        self.screen_center_y = 0

        self.manager = None
        self.v_box: arcade.gui.UIBoxLayout = None
        self.console_active = False

        self.debugging_console = None
        self.debugging_console_tex_inp = None
        self.debugging_console_tex_out = None
        self.debugging_console_tex = None

        self.tic = 0

    def on_show_view(self):
        """Called when the current is switched to this view."""
        self.setup()

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.manager = arcade.gui.UIManager()
        self.v_box = arcade.gui.UIBoxLayout()
        self.debugging_console = arcade.gui.UIInputText(text=">", width=self.main_window.width, height=25)
        tex = arcade.texture.Texture("tex creator")
        self.debugging_console_tex_inp = tex.create_filled(color=(100, 0, 0, 150), name="debug console in",
                                                           size=(self.main_window.width, 25))
        self.debugging_console_tex_out = tex.create_filled(color=(0, 100, 0, 150), name="debug console out",
                                                           size=(self.main_window.width, 25))
        self.debugging_console_tex = self.debugging_console.with_background(self.debugging_console_tex_inp)
        self.v_box.add(self.debugging_console_tex)

        self.manager.add(arcade.gui.UIAnchorWidget(child=self.v_box, anchor_y="bottom"))
        self.manager.enable()

        self.game_scene = arcade.Scene()

        self.camera = arcade.Camera(self.main_window.width, self.main_window.height)

        self.camera_sprite = arcade.Sprite(str(ASSET_PATH / "tiles" / "pnj.png"))
        # this can be renamed to player sprite, if player sprite is decided to be made.
        self.camera_sprite = arcade.Sprite(str(ASSET_PATH / "tiles" / "pnj.png"))
        # self.camera_sprite.center_x = 400
        # self.camera_sprite.center_y = 300
        self.camera_sprite.center_x = 0
        self.camera_sprite.center_y = 0
        self.game_scene.add_sprite("Camera", self.camera_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.camera_sprite, gravity_constant=0)

        self.light_layer = LightLayer(self.main_window.width, self.main_window.height)

        self.tic = 0

    def on_draw(self):
        """Render the screen."""
        self.clear()

        self.camera.use()
        # self.game_scene.draw()
        if self.main_window.mouse_left_is_pressed:
            pass

        with self.light_layer:
            self.game_scene.draw()
        self.light_layer.draw(ambient_color=(255, 255, 255))

        if self.console_active:
            self.manager.draw()

    def on_key_press(self, key, _):
        """Called whenever a key is pressed."""
        # using change because if it is changed to player physics engine is required.
        if key in (arcade.key.UP, arcade.key.W):
            self.camera_sprite.change_y = CAMERA_MOVEMENT_SPEED
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.camera_sprite.change_y = -CAMERA_MOVEMENT_SPEED
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.camera_sprite.change_x = -CAMERA_MOVEMENT_SPEED
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.camera_sprite.change_x = CAMERA_MOVEMENT_SPEED
        elif key == arcade.key.F4:
            self.manager.enable()
            if self.console_active:
                self.manager.disable()
            self.console_active = not self.console_active
        elif key == arcade.key.ENTER:
            if not self.console_active:
                return
            if self.debugging_console.text[1:] in ('clear', 'cls'):
                self.v_box.clear()
                self.debugging_console = arcade.gui.UIInputText(text=">", width=self.main_window.width, height=25)
                self.debugging_console_tex = self.debugging_console.with_background(self.debugging_console_tex_inp)
                self.v_box.add(self.debugging_console_tex)
            else:
                out = arcade.gui.UILabel(text=str(eval(f"{self.debugging_console.text[1:]}")),
                                         width=self.main_window.width, height=25, text_color=(255, 255, 255))
                out_tex = out.with_background(self.debugging_console_tex_out)
                self.v_box.remove(self.debugging_console_tex)
                prev = arcade.gui.UILabel(text=self.debugging_console.text,
                                          width=self.main_window.width, height=25, text_color=(0, 0, 0))
                prev_tex = prev.with_background(self.debugging_console_tex_inp)
                self.v_box.add(prev_tex)
                self.v_box.add(out_tex)
                self.debugging_console = arcade.gui.UIInputText(text=">", width=self.main_window.width, height=25)
                self.debugging_console_tex = self.debugging_console.with_background(self.debugging_console_tex_inp)
                self.v_box.add(self.debugging_console_tex)

    def on_key_release(self, key, _):
        """Called when the user releases a key."""
        if key in (arcade.key.UP, arcade.key.W):
            self.camera_sprite.change_y = 0
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.camera_sprite.change_y = 0
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.camera_sprite.change_x = 0
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.camera_sprite.change_x = 0

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, _buttons: int, _modifiers: int):
        """Called when the mouse is dragged."""
        if INVERT_MOUSE:
            self.camera_sprite.center_x -= dx
            self.camera_sprite.center_y -= dy
        else:
            self.camera_sprite.center_x += dx
            self.camera_sprite.center_y += dy

    def on_mouse_motion(self, x, y, dx, dy):
        self.main_window.mouse_x = x
        self.main_window.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.main_window.mouse_left_is_pressed = True
            actual_x = x + self.screen_center_x
            actual_y = y + self.screen_center_y

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.main_window.mouse_left_is_pressed = False

    def center_camera_to_camera(self):
        """Centers camera to the camera sprite."""
        self.screen_center_x = self.camera_sprite.center_x - \
                               (self.camera.viewport_width / 2)
        self.screen_center_y = self.camera_sprite.center_y - \
                               (self.camera.viewport_height / 2)

        camera_centered = self.screen_center_x, self.screen_center_y
        self.camera.move_to(camera_centered)

    
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

    def __init__(self, main_window: arcade.Window, win_loose=''):
        super().__init__(main_window)
        self.main_window = main_window
        self.v_box = None
        self.manager = None
        self.win_loose_message = win_loose
        self.background = arcade.load_texture(str(ASSET_PATH / "titles" / "victory_background.jpg"))

    def on_show_view(self) -> None:
        """Called when the current is switched to this view."""
        self.setup()

    def setup(self) -> None:
        """Set up the game variables. Call to re-start the game."""
        self.v_box = arcade.gui.UIBoxLayout(space_between=10)
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        win_loose_button = arcade.gui.UIFlatButton(
            text=self.win_loose_message, width=200, style=STYLE_GOLDEN_TANOI)

        restart_button = arcade.gui.UIFlatButton(
            text="Restart", width=200, style=STYLE_GOLDEN_TANOI)
        restart_button.on_click = self._on_click_restart_button

        exit_button = arcade.gui.UIFlatButton(
            text="Exit", width=200, style=STYLE_GOLDEN_TANOI)
        exit_button.on_click = self._on_click_exit_button

        self.v_box.add(win_loose_button)
        self.v_box.add(restart_button)
        self.v_box.add(exit_button)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                child=self.v_box
            )
        )

    def on_draw(self) -> None:
        """Called when this view should draw."""
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        self.manager.draw()

    def _on_click_restart_button(self, _: arcade.gui.UIOnClickEvent) -> None:
        game = Game(self.main_window)
        self.main_window.show_view(game)

    def _on_click_exit_button(self, _: arcade.gui.UIOnClickEvent) -> None:
        self.main_window.close()
        arcade.exit()

    def on_hide_view(self):
        self.manager.disable()