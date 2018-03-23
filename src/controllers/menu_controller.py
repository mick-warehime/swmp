import warnings

from controllers.base import Controller


class MenuController(Controller):
    def update(self) -> None:
        self.keyboard.handle_input()

    def set_player_data(self, data: 'HumanoidData') -> None:
        warnings.warn('set_player_data undefined for MenuController.')

    def draw(self) -> None:
        pass
