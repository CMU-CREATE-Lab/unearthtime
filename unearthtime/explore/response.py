"""The response module defines objects representing the various responses from querying the DOM."""

from __future__ import annotations

from io import BytesIO
from time import sleep
from typing import Iterable, Union

from PIL import Image
from cv2 import cvtColor, COLOR_BGR2RGB, COLOR_BGR2GRAY
from numpy import array
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.remote.webelement import WebElement as Element

from .._algae.exceptions import UnearthtimeException
from .._algae.utils import raiseif


class MissType(type):
    """Metaclass representing a failed response from the DOM."""

    def __bool__(cls): return False

    def __call__(cls): return cls

    def __hash__(cls): return hash(id(cls))

    def __repr__(cls): return 'Miss'


class Miss(metaclass=MissType):
    """A failed response from the DOM."""


class Hit:
    """A successful response from the DOM."""

    def __init__(self, element: Element):
        self._element = element
        self.__display = element.parent.execute_script('return arguments[0].style.display', element)

    def __eq__(self, other: Union[Element, 'Hit']):
        return self._element == other if isinstance(other, Element) else self._element == other._element

    def __getattr__(self, attr: str):
        """Exposes `HTML` and `javascript` attributes, allowing access via dot-notation.

        Parameters:
            - `attr` : `str`

        Returns:
            - `str`

        Raises:
            - `AttributeError` : Invalid `attr`.

        Notes:
            - `id` and `class` are special cases and these tag attributes can be accessed
            by appending an underscore
        """
        if hasattr(self._element, attr):
            return self._element.__getattribute__(attr)
        else:
            if attr in ('id_', 'class_'):
                attr = attr[1:-1]

            if (eattr := self.__getitem__(attr)) is not None:
                return eattr
            elif (jattr := self._element.parent.execute_script('return arguments[0].%s' % attr, self._element)) is not None:
                return Hit(jattr) if isinstance(jattr, Element) else jattr
            else:
                raise AttributeError(':[%r]: Invalid attribute.' % attr)

    def __getitem__(self, attr: str):
        """Retrieves a tag attribute of the element.

        Parameters:
            - `attr`: `str`

        Returns:
            - `str`
        """
        return self.get_attribute(attr)

    def __repr__(self):
        return '%s[%s]' % (Hit.__name__, self._id)

    @property
    def driver_session_id(self):
        """The session if of the Selenium driver for this element."""
        return self._element.parent.session_id

    @property
    def selenium_id(self):
        """The internal Selenium id of the element."""
        return self._element.id

    @property
    def tag_name(self) -> str:
        """The tag type of this element."""
        return self._element.parent.execute_script('return arguments[0].tagName', self._element)

    def click(self, wait: Union[float, int]):
        """Clicks the element.

        Notes:
            - If the element is not in view when the first click is tried,
            an attempt will be made to scroll into view, before trying to
            click it again.
        """
        try:
            self._element.click()
        except (ElementClickInterceptedException, ElementNotInteractableException):
            self._element.parent.execute_script('arguments[0].scrollIntoView(); arguments[0].click();', self._element)

        if wait > 0:
            sleep(wait)

    def hide(self):
        """Hides the element by setting the display in the style attribute to 'none'."""
        if self.__display != 'none':
            self._element.parent.execute_script("arguments[0].style.display='none'", self._element)

    def next_sibling(self):
        """The sibling element following this element.

        Returns:
            - `Hit`
        """
        return Hit(self._element.parent.execute_script('return arguments[0].nextElementSibling', self._element))

    def parent_element(self):
        """The parent of this element in the DOM.

        Returns:
            - `Hit`
        """
        return Hit(self._element.find_element_by_xpath('./..'))

    def previous_sibling(self):
        """The sibling element preceding this element.

        Returns:
            - `Hit`
        """
        return Hit(self._element.parent.execute_script('return arguments[0].previousElementSibling', self._element))

    def reset_display(self):
        """Sets the display in the style of this element back to it's original state."""
        self._element.parent.execute_script("arguments[0].style.display='%s'" % self.__display, self._element)

    def screenshot(self, mode: str = 'png'):
        """Takes a screenshot of this element.

        Raises:
            - `UnearthtimeException` : Parent `WebDriver` isn't a chrome driver.

        Notes:
            - This is a Chrome specific capability
        """
        raiseif(
            self._element.parent != 'chrome',
            UnearthtimeException('Element screenshot only available for Chrome driver.')
        )

        if mode == 'png' or mode == 'PNG':
            return self._element.screenshot_as_png
        elif mode == 'base64':
            return self._element.screenshot_as_base64
        elif mode == 'img' or mode == 'image':
            return Image.open(BytesIO(self._element.screenshot_as_png))
        elif mode == 'array' or mode == 'ndarray':
            return array((Image.open(BytesIO(self._element.screenshot_as_png))))
        elif mode == 'rgb' or mode == 'RGB':
            return cvtColor(array(Image.open(BytesIO(self._element.screenshot_as_png))), COLOR_BGR2RGB)
        elif mode == 'gray' or mode == 'grey':
            return cvtColor(array(Image.open(BytesIO(self._element.screenshot_as_png))), COLOR_BGR2GRAY)


class HitList(tuple):
    """A collection of successful responses from the DOM."""

    def __new__(cls, hits: Iterable[Union[Element, Hit]] = None):
        if hits:
            return tuple.__new__(cls, (hit if isinstance(hit, Hit) else Hit(hit) for hit in hits))
        else:
            return tuple.__new__(cls)

    def __repr__(self):
        return '%s[%s]' % (HitList.__name__, '\n\t%s\n' % '\n\t'.join(map(str, self)) if bool(self) else '')
