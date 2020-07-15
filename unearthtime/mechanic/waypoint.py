from __future__ import annotations
from _algae.deco import returnonexception
from _algae.utils import until
from .operator import SelectableOperator

from environment import Environment
from explore.image import Thumbnail
from explore.response import Miss
from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webelement import WebElement as Element
from time import sleep
from typing import Callable, Iterable, Union

class Waypoint(SelectableOperator):

	def __init__(self, waypoint_id: str, env: Environment):
		super().__init__(env)

		self.__thumbnail = None
		self.__title = ''
		self.__waypoint = None
		self.__waypoint_id = waypoint_id

	def __repr__(self): return '%s[%s]' % (Waypoint.__name__, self.__title)

	@staticmethod
	def waypoints_of(env: Environment): return [ Waypoint(waypoint.id_, env) for waypoint in waypoints] if bool(env) and ( waypoints := env['Waypoints'] ) else []
	
	@property
	def id(self) -> str: return self.__waypoint_id

	@property
	def thumbnail(self) -> str: return self.__thumbnail

	@property
	def title(self) -> str: return self.__title

	@returnonexception(False, ElementNotInteractableException)
	def inform(self):
		if self._has_been_informed:
			return bool(self._env)
		elif self.is_informable() and (waypoint := self._env['Waypoint', self.__waypoint_id]):
			self.__waypoint = waypoint
			self.__id = waypoint.id_
			self.__title = self._env['WaypointTitle', self.__waypoint_id].text
			
			src = self._env['WaypointThumbnail', self.__waypoint_id].src

			wstart = src.find('width=') + 6
			hstart = src.find('height=') + 7
			wstop = src.find('&', wstart)
			hstop = src.find('&', hstart)

			w, h = int(src[wstart:wstop]), int(src[hstart:hstop])

			self.__thumbnail = Thumbnail(src, w, h)

			self._has_been_informed = True

			return True
		else:
			return False

	@returnonexception(False, StaleElementReferenceException)
	def select(self):
		if self.inform():
			self.__waypoint.click()

			until(lambda: not self._env.is_moving_to_waypoint(), cycles=10)