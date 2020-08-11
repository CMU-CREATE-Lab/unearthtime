from __future__ import annotations

from abc import ABC, abstractmethod

from .._algae.exceptions import UnearthtimeException
from .._algae.utils import raiseif
from ..earthtime import EarthTime

_InvalidAttributes = {
    'driver',
    'explore',
    'goto',
    'load',
    'quit',
    'release_driver',
    'screenshot',
    'screenshot_and_save',
    'get',
    'back',
    'close',
    'forward',
    'refresh'
}


class Tool(ABC):

    def __init__(self, earthtime: EarthTime):
        raiseif(
            earthtime is None or bool(earthtime),
            UnearthtimeException('Invalid or inactive EarthTime page.')
        )

        self._earthtime = earthtime
        self._informed = False

    def informable(self) -> bool:
        return not self.__informed and bool(self._earthtime)

    @abstractmethod
    def inform(self) -> bool: return False

    def reinform(self) -> bool:
        self._informed = False
        return self.inform()


class SelectableTool(Tool):

    @abstractmethod
    def select(self): pass
