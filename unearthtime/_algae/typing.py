from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webelement import WebElement as Element
from typing import Callable, Iterable, Union


ElementPredicate = Callable[[Union[Element, Iterable[Element]]], bool]
WebObject = Union[Driver, Element]

class MissType(type):
	def __bool__(cls): return False

	def __call__(cls): return cls

	def __hash__(cls): return hash(id(cls))

	def __repr__(cls): return 'Miss'