"""Objects representing possible responses from a request to the DOM"""
from __future__ import annotations
from _algae.typing import ElementPredicate, MissType
from _algae.utils import istrue

from cv2 import cvtColor, COLOR_BGR2RGB, COLOR_BGR2GRAY
from functools import reduce
from io import BytesIO
from numpy import array
from PIL import Image
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.remote.webelement import WebElement as Element
from time import sleep

class Miss(metaclass=MissType):
    """Represents a missed request to the DOM
    
    Notes:
    - `Miss` is always `False`.
    """
	
class Hit:
    """A successful return from a request."""

    def __init__(self, element: Element):
        self._element = element 
        self.__display = self._parent.execute_script('return arguments[0].style.display', element)

    def __getattr__(self, attr: str):
        """Allows the `HTML` and js attributes of an element to be accessed using dot-notation.

        Parameters:
        - `attr` : `str`
            * The name of a tag or javascript attribute

        Returns:
        - `str`
            * The value of the attribute

        Exceptions:
        - `AttributeError`
            * If the element doesn't have the attribute
        
        Notes:
        - `id` and `class` are special cases and can be accessed by appending an 
        underscore to the end
        """
        if hasattr(self._element, attr):
            return self._element.__getattribute__(attr)
        
        if attr == 'id_' or attr == 'class_':
            attr = attr.rstrip('_')

        if (attr := self.__getitem__(attr)) is not None:
            return attr
        elif (attr := self._parent.execute_script('return arguments[0].%s;' % attr, self)) is not None:
            return attr
        else:
            raise AttributeError(
                ':[%r]: Input is not an attribute of this element.' % attr)

    def __getitem__(self, attr: str):
        """Retrieves an attribute of the element.
        
        Parameters:
        - `attr` : `str`
            * The name of a tag attribute

        Returns:
        - `str`
            * The value of the attribute

        Notes:
        - Where `Hit.__getattr__(attr)` will raise an `AttributeError` if the attribute isn't present, this method will return `None`
        """
        return self.get_attribute(attr)

    def __repr__(self): return 'Hit[%s]' % self._id

    @property
    def selenium_id(self):
        """The Selenium specific id of this element""" 
        return self._id

    @property
    def session(self):
        """The Selenium specific session id of the `WebDriver` for this element""" 
        return self._element._parent.session_id

    def apply(self, method: Callable): 
        """Applies a method to this element
        
        Parameters:
        - `method` : `Callable(Element)`
            * A method that can accept a `WebElement` as it's only argument

        Returns:
        - `Any`
            * The result of `method(self)`

        """
        return method(self)

    def click(self, wait: Union[float, int] = 0.5):
        """Clicks this element if it is clickable
        
        Parameters:
        - `wait` : `float`, `int` = `0.5`
            * The amount of time to wait after clicking an element
        """
        try:
            self._element.click()
        except (ElementClickInterceptedException, ElementNotInteractableException):
            self._element._parent.execute_script(
                'arguments[0].scrollIntoView(); arguments[0].click();', self._element)

        if isinstance(wait, (int, float)) and wait > 0:
            sleep(wait)

    def hide(self):
        """Hides this element if it is displayed"""
        if self.__display != 'none':
            self._element._parent.execute_script("arguments[0].style.display='none'", self._element)

    def if_(self, condition: Union[bool, ElementPredicate]):
        """Checks a condition or applies one to this element.

        Parameters:
        - `condition`
            * A `bool` or predicate that can accept a `WebElement` as it's only parameter

        Returns:
        - `Hit`, `Miss`
            * This element if `condition`, `condition(self)` is `True`, `Miss` otherwise
        """
        return self if istrue(condition) or (
            callable(condition) and istrue(condition(self))) else Miss

    def reset_display(self):
        """Sets the display property back to what it was if one was present"""
        self._element._parent.execute_script("arguments[0].style.display='%s';" % self.__display)

    def screenshot(self, mode='png'):
        """Takes a screenshot of the element

        Parameters:
        - `mode`: `str` = `'png'`
            * One of: 
                * 'base64' :&#8658; `str`
                * 'png' :&#8658; `bytes` 
                * 'image' :&#8658; `PIL.Image`
                * 'array' :&#8658; `numpy.ndarray`
                * 'rgb' :&#8658; `numpy.ndarray`
                * 'gray' :&#8658; `numpy.ndarray`
        """
        if mode == 'png':
            return self._element.screenshot_as_png
        elif mode == 'base64':
            return self._element.screenshot_as_base64
        elif mode == 'img':
            return Image.open(BytesIO(self._element.screenshot_as_png))
        elif mode == 'array':
            return array(Image.open(BytesIO(self._element.screenshot_as_png)))
        elif mode == 'rgb':
            return cvtColor(array(Image.open(BytesIO(self._element.screenshot_as_png))), COLOR_BGR2RGB)
        elif mode == 'gray':
            return cvtColor(array(Image.open(BytesIO(self._element.screenshot_as_png))), COLOR_BGR2GRAY)
        

    def verify(self, condition: ElementPredicate):
        """Applies a condition to this element

        Parameters:
        - `condition`
            * A predicate that can accept a `WebElement` as it's only parameter

        Returns:
        - `True`, `False`
            The result of `condition(self)`
        """ 
        return condition(self)


class HitList(tuple):
    """A tuple of successful responses from a request"""

    def __new__(cls, hits: Iterable[Element] = None):
        if hits:
            return tuple.__new__(cls, (hit if isinstance(hit, Hit) else Hit(hit) for hit in hits))
        else:
            return tuple.__new__(cls)

    def __bool__(self): return len(self) > 0

    def __getitem__(self, key: Union[Callable[[Element], bool], int]): 
        """Retrieves either a specific hit or applies a condition to all of them
        
        Parameters:
        - `key` : `int`, `Callable(Element)` &#8658; `bool`
            * Index of an element or predicate that can accept a `WebElement` as its only parameter

        Returns:
        - `Hit`
            * If `key` is an `int`, the hit at that index is returned

        - `HitList`
            * If `key` is a condition, a list of `Hit`s for which `conditional(Hit)` is `True`
        """
        return HitList(
        hit for hit in self if istrue(key(hit))) if callable(key) else super().__getitem__(key)

    def __add__(self, x): return HitList(tuple(self) + x)

    def __repr__(self): return '%s[\n\t%s\n]' % (HitList.__name__, '\n\t'.join(map(str, self))) if len(self) > 0 else '%s[]' % HitList.__name__

    def apply(self, method: Callable): 
        """Applies a method to each hit

        Parameters:
        - `method` : `Callable(Element)`
            * A method that can accept a `WebElement` as it's only argument

        Returns:
        - `list`
            * The result of applying the method
        """
        return list(map(method, self))

    def verify(self, condition: ElementPredicate):
        """Applies a conditional to each hit

        Parameters:
        - `method` : `Callable(Element)`
            * A predicate that can accept a `WebElement` as it's only argument


        Returns:
        - `True`, `False`
            * The result of `and`-ing  the results of `condition(Hit)` for each hit
        """
        return reduce(lambda x, y: x and y, [istrue(condition(hit)) for hit in self], True)

    def where(self, condition: Union[bool, ElementPredicate]):
        """Checks a condition or applies one to each hit

        Parameters:
        - `condition` : `int`, `Callable(Element)` &#8658; `bool`
            * Index of an element or predicate that can accept a `WebElement` as its only parameter

        Returns:
        - `HitList`
            * This list if `condition` is `True` or a list of hits where `condition(Hit)` is `True`. An empty list returned otherwise
        """
        if isinstance(condition, bool):
            return self if condition else HitList()
        else:
            return HitList(filter(condition, self))