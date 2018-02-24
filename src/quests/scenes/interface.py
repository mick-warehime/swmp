from typing import Tuple, List

from controllers.base import Controller
from quests.resolutions import Resolution

ControllerAndResolutions = Tuple[Controller, List[Resolution]]


class Scene(object):
    """Instantiates a Controller and Resolutions to represent a scene.

    These are like factory methods.
    """
    def make_controller_and_resolutions(self) -> ControllerAndResolutions:
        raise NotImplementedError
