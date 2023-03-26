import arcade

from config import GameConfig
from window import Menu, Window, WinLooseMenu

if __name__ == "__main__":
    game = Window(GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT, GameConfig.SCREEN_TITLE)
    menu = Menu(game)
    win_loose = WinLooseMenu(game)
    game.show_view(menu)
    # music = arcade.Sound(str(ASSET_PATH / "music" / "frontier.ogg"))
    # music.play(MUSIC_VOLUME, loop=True)
    arcade.run()
