from __future__ import annotations

from _algae.utils import istrue

from .locator import Locator

from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webelement import WebElement as Element
from typing import Callable, Union

class Wait:

	def __init__(self, locator: Union[Element, Locator], condition: Callable[[Element], bool]):
		self.__locator = locator
		self.__condition = condition

	def __call__(self, driver: Driver):
		if isinstance(self.__locator, Locator):
			element = __locator(driver)
		else:
			element = self.__locator

		if istrue(self.__condition(element)):
			return element
		else:
			return False

class CheckedLayer(Wait):

	def __new__(cls, layer: Element):
		return Wait.__new__(cls, layer, lambda x: x.checked)