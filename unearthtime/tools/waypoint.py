from __future__ import annotations

from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException

from .tool import SelectableTool
from .._algae.deco import returnonexception
from .._algae.utils import until
from ..earthtime import EarthTime
from ..imaging.image import Thumbnail, Dimension


class Waypoint(SelectableTool):

    def __init__(self, waypoint_id: str, earthtime: EarthTime):
        super().__init__(earthtime)
        self.__thumbnail = None
        self.__title = ''
        self.__waypoint = None
        self.__waypoint_id = waypoint_id

    def __repr__(self):
        return f'{Waypoint.__name__}[{self.__title}]'

    @classmethod
    def informed(cls, waypoint_id: str, earthtime: EarthTime):
        waypoint = cls(waypoint_id, earthtime)
        waypoint.inform()

        return waypoint

    @staticmethod
    def waypoints(earthtime: EarthTime) -> list:
        return [Waypoint(waypoint.id_, earthtime) for waypoint in waypoints] if bool(earthtime) and (waypoints := earthtime.Waypoints) else []

    @property
    def thumbnail(self) -> Thumbnail:
        return self.__thumbnail

    @property
    def title(self):
        return self.__title

    @property
    def waypoint_id(self):
        return self.__waypoint_id

    @returnonexception(False, ElementNotInteractableException)
    def inform(self) -> bool:
        if self._informed:
            return bool(self._earthtime)
        elif self.informable() and (waypoint := self._earthtime['Waypoint', self.__waypoint_id]):
            self.__waypoint = waypoint
            self.__waypoint_id = waypoint.id_
            self.__title = self._earthtime['WaypointTitle', self.__waypoint_id].text

            src = self._earthtime['WaypointThumbnail', self.__waypoint_id]

            wstart, hstart = src.find('width=') + 6, src.find('height=') + 7
            wstop, hstop = src.find('&', wstart), src.find('&', hstart)

            dim = Dimension(int(src[wstart:wstop]), int(src[hstart:hstop]))

            self.__thumbnail = Thumbnail(src, dim)
            self._informed = True

        return self._informed

    @returnonexception(None, StaleElementReferenceException)
    def select(self):
        if self.inform():
            self.__waypoint.click()

            until(lambda: not self._earthtime.isMovingToWaypoint(), wait=0.25, cycles=20)
