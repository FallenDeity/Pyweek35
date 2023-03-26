import arcade

from src.utils.constants import GameConfig
from src.window import Menu, Window, WinLoseMenu

if __name__ == "__main__":
    game = Window(GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT, GameConfig.SCREEN_TITLE)
    menu = Menu(game)
    win_lose = WinLoseMenu(game)
    game.show_view(menu)
    arcade.run()
