"""The query module defines methods for handling requests and responses from the DOM.

This module provides finder methods for querying the DOM. Each finder method
is named by the form of its `query`. All `f*` methods find one element. All
`fx*` methods find all elements matching the query. `*` here can be any one of
`class`, `css`, `id`, `name`, `tag`, or `xpath`, corresponding to the
query being a *class name*, *css selector*, *id*, *name*, *tag*, or *xpath*.

If `f*(query)` represents a finder method, it has the form
`f*(query) -> lambda parent: parent.find_element_by_*(query)`, where `parent`
can be a `WebDriver` or `WebElement`.

The response from these methods will be either a `Hit`, `HitList` or `Miss`.

These methods all take an optional `until` argument representing a condition the
found element(s) must fulfill. The form of this argument must be a `Callable`
initialized witht the element(s) found by the query.


Attributes:
    - `ResponseType` : `Hit`, `HitList`, `Miss`
    - `WaitType` : `(Driver)` -> `Hit`, `HitList`, `False`
    - `WebObject` : `WebDriver`, `WebElement`
"""
from __future__ import annotations

from collections import namedtuple
from enum import Enum
from typing import Callable, Literal, Union

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webelement import WebElement as Element
from selenium.webdriver.support.ui import WebDriverWait

from .response import Hit, HitList, Miss, MissType
from .._algae.deco import returnonexception
from .._algae.exceptions import UnearthtimeException

__all__ = ['By', 'fclass', 'fcss', 'fid', 'find', 'find_all', 'fname', 'ftag', 'fxpath',
           'fxclass', 'fxcss', 'fxid', 'fxname', 'fxtag', 'fxxpath', 'response_of', 'wait_for']

ResponseType = Union[Hit, HitList, MissType]
WaitType = Callable[[Driver], Union[Hit, HitList, Literal[False]]]
WebObject = Union[Driver, Element]


def response_of(method: Callable): return returnonexception(Miss, (NoSuchElementException, TimeoutException))(method)


def wait_for(webobj: WebObject, timeout: Union[float, int] = 10, poll_freq: Union[float, int] = 0.5):
    return WebDriverWait(webobj, timeout, poll_freq) if isinstance(webobj, Driver) else WebDriverWait(webobj.parent, timeout, poll_freq)


_By = namedtuple('_By', ['canonical_name', 'display_name'])


class By(Enum):
    """What the text of a query represents when locating an element."""
    CLASS = _By('class', 'by-class-name')
    CSS = _By('css_selector', 'by-css-selector')
    ID = _By('id', 'by-id')
    NAME = _By('name', 'by-name')
    TAG = _By('tag', 'by-tag-name')
    XPATH = _By('xpath', 'by-xpath')


def fclass(query: str, until: WaitType = None):
    """Finds an element by class name.

    Parameters:
        - `query` : `str`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `(Union[WebDriver, WebElement])` -> `Hit`, `HitList`, `Miss`
    """
    if not until:
        return response_of(lambda parent: Hit(parent.find_element_by_class_name(query)) if parent else Miss)
    else:
        return response_of(lambda parent: Hit(wait_for(parent).until(until(parent.find_element_by_class_name(query))) if parent else Miss))


def fcss(query: str, until: WaitType = None):
    """Finds an element by css selector.

    Parameters:
        - `query` : `str`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `(Union[WebDriver, WebElement])` -> `Hit`, `HitList`, `Miss`
    """
    if not until:
        return response_of(lambda parent: Hit(parent.find_element_by_css_selector(query)) if parent else Miss)
    else:
        return response_of(lambda parent: Hit(wait_for(parent).until(until(parent.find_element_by_css_selector(query))) if parent else Miss))


def fid(query: str, until: WaitType = None):
    """Finds an element by its id.

    Parameters:
        - `query` : `str`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `(Union[WebDriver, WebElement])` -> `Hit`, `HitList`, `Miss`
    """
    if not until:
        return response_of(lambda parent: Hit(parent.find_element_by_id(query)) if parent else Miss)
    else:
        return response_of(lambda parent: Hit(wait_for(parent).until(until(parent.find_element_by_id(query))) if parent else Miss))


def fname(query: str, until: WaitType = None):
    """Finds an element by name.

    Parameters:
        - `query` : `str`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `(Union[WebDriver, WebElement])` -> `Hit`, `HitList`, `Miss`
    """
    if not until:
        return response_of(lambda parent: Hit(parent.find_element_by_name(query)) if parent else Miss)
    else:
        return response_of(lambda parent: Hit(wait_for(parent).until(until(parent.find_element_by_name(query))) if parent else Miss))


def ftag(query: str, until: WaitType = None):
    """Finds an element by tag name.

    Parameters:
        - `query` : `str`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `(Union[WebDriver, WebElement])` -> `Hit`, `HitList`, `Miss`
    """
    if not until:
        return response_of(lambda parent: Hit(parent.find_element_by_tag_name(query)) if parent else Miss)
    else:
        return response_of(lambda parent: Hit(wait_for(parent).until(until(parent.find_element_by_tag_name(query))) if parent else Miss))


def fxpath(query: str, until: WaitType = None):
    """Finds an element by xpath.

    Parameters:
        - `query` : `str`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `(Union[WebDriver, WebElement])` -> `Hit`, `HitList`, `Miss`
    """
    if not until:
        return response_of(lambda parent: Hit(parent.find_element_by_xpath(query)) if parent else Miss)
    else:
        return response_of(lambda parent: Hit(wait_for(parent).until(until(parent.find_element_by_xpath(query))) if parent else Miss))


def fxclass(query: str, until: WaitType = None):
    """Finds elements by class name.

    Parameters:
        - `query` : `str`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `(Union[WebDriver, WebElement])` -> `Hit`, `HitList`, `Miss`
    """
    if not until:
        return response_of(lambda parent: HitList(parent.find_elements_by_class_name(query)) if parent else Miss)
    else:
        return response_of(lambda parent: HitList(wait_for(parent).until(until(parent.find_elements_by_class_name(query))) if parent else Miss))


def fxcss(query: str, until: WaitType = None):
    """Finds elements by css selector.

    Parameters:
        - `query` : `str`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `(Union[WebDriver, WebElement])` -> `Hit`, `HitList`, `Miss`
    """
    if not until:
        return response_of(lambda parent: HitList(parent.find_elements_by_css_selector(query)) if parent else Miss)
    else:
        return response_of(lambda parent: HitList(wait_for(parent).until(until(parent.find_elements_by_css_selector(query))) if parent else Miss))


def fxid(query: str, until: WaitType = None):
    """Finds elements by id.

    Parameters:
        - `query` : `str`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `(Union[WebDriver, WebElement])` -> `Hit`, `HitList`, `Miss`
    """
    if not until:
        return response_of(lambda parent: HitList(parent.find_elements_by_id(query)) if parent else Miss)
    else:
        return response_of(lambda parent: HitList(wait_for(parent).until(until(parent.find_elements_by_id(query))) if parent else Miss))


def fxname(query: str, until: WaitType = None):
    """Finds elements by name.

    Parameters:
        - `query` : `str`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `(Union[WebDriver, WebElement])` -> `Hit`, `HitList`, `Miss`
    """
    if not until:
        return response_of(lambda parent: Hit(parent.find_elements_by_name(query)) if parent else Miss)
    else:
        return response_of(lambda parent: HitList(wait_for(parent).until(until(parent.find_elements_by_name(query))) if parent else Miss))


def fxtag(query: str, until: WaitType = None):
    """Finds elements by tag name.

    Parameters:
        - `query` : `str`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `(Union[WebDriver, WebElement])` -> `Hit`, `HitList`, `Miss`
    """
    if not until:
        return response_of(lambda parent: Hit(parent.find_elements_by_tag_name(query)) if parent else Miss)
    else:
        return response_of(lambda parent: HitList(wait_for(parent).until(until(parent.find_elements_by_tag_name(query))) if parent else Miss))


def fxxpath(query: str, until: WaitType = None):
    """Finds elements by xpath.

    Parameters:
        - `query` : `str`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `(Union[WebDriver, WebElement])` -> `Hit`, `HitList`, `Miss`
    """
    if not until:
        return response_of(lambda parent: HitList(parent.find_elements_by_xpath(query)) if parent else Miss)
    else:
        return response_of(lambda parent: HitList(wait_for(parent).until(until(parent.find_elements_by_xpath(query))) if parent else Miss))


def find(query: str, by: By, parent: WebObject, until: WaitType = None) -> ResponseType:
    """General finder method for a single element.

    Parameters:
        - `query` : `str`
        - `by` : `By`
        - `parent` : `WebDriver`, `WebElement`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `Hit`, `HitList`, `Miss`

    Raises:
        - `UnearthtimeException` : Invalid `by` enum.
    """
    if by == By.ID:
        return fid(query, until)(parent)
    if by == By.CSS:
        return fcss(query, until)(parent)
    elif by == By.XPATH:
        return fxpath(query, until)(parent)
    elif by == By.CLASS:
        return fclass(query, until)(parent)
    elif by == By.TAG:
        return ftag(query, until)(parent)
    elif by == By.NAME:
        return fname(query, until)(parent)
    else:
        raise UnearthtimeException(':[%r]: Unrecognized `By` flag.')


def find_all(query: str, by: By, parent: WebObject, until: WaitType = None) -> ResponseType:
    """General finder method for a list of elements.

    Parameters:
        - `query` : `str`
        - `by` : `By`
        - `parent` : `WebDriver`, `WebElement`
        - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

    Returns:
        - `Hit`, `HitList`, `Miss`
    """
    if by == By.ID:
        return fxid(query, until)(parent)
    if by == By.CSS:
        return fxcss(query, until)(parent)
    elif by == By.XPATH:
        return fxxpath(query, until)(parent)
    elif by == By.CLASS:
        return fxclass(query, until)(parent)
    elif by == By.TAG:
        return fxtag(query, until)(parent)
    elif by == By.NAME:
        return fxname(query, until)(parent)
    else:
        raise UnearthtimeException(':[%r]: Unrecognized `By` flag.')
