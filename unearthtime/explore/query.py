"""Handles requests and responses to the DOM.

This module provides finder methods for retrieving elements
from a webpage.

Each finder is named by the form of its `query`. All `f*`
methods find one (1) element. All `fx*` methods find all
elements matching the query. `*` can be one of 
`class`, `css`, `id`, `name`, `tag`, or `xpath`,
corresponding to the *class name*, *css selector*, *id*, *name*,
*tag name*, or *xpath* respectively of the element(s).

If `f(query)` is a finder method, it has the general form: 
`f(query) => lambda parent: parent.find_element_by_*(query)`.
Each finder method returns another method expecting either
a **Selenium** `WebDriver` or `WebElement`.

The response of these returned methods is one of three objects:

- `Hit`
- `HitList`
- `Miss`

Attributes:

- `responseof`
*   lambda expression that wraps a method in the `returnonexception` decorator.

- `waitfor`
*   lambda expression that returns a **Selenium** `WebDriverWait`
    object for doing explicit waits with elements.

Typing:

- `WebObject`: `WebDriver`, `WebElement`
- `Response`: `Hit`, `HitList`, `Miss`
- `Wait`: `Callable(Driver) :&#8658; `Hit`, `HitList`, `False`
"""

from __future__ import annotations

from _algae.deco import returnonexception
from _algae.exceptions import UnearthtimeException
from _algae.typing import ElementPredicate, WebObject

from .response import Hit, HitList, Miss

from enum import Enum
from richenum import RichEnumValue
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webelement import WebElement as Element
from selenium.webdriver.support.ui import WebDriverWait
from typing import Callable, Literal, Union

__all__ = ['By', 'fclass', 'fcss', 'fid', 'fname', 'ftag', 'fxpath', 'fxclass', 'fxcss', 'fxid', 'fxname', 'fxtag', 'fxxpath', 'find', 'findall']

Response = Union[Hit, HitList, Miss]
Wait = Callable[[Driver], Union[Hit, HitList, Literal[False]]]

responseof = lambda method: returnonexception(Miss, (NoSuchElementException, TimeoutException))(method)

waitfor = lambda webobj: WebDriverWait(webobj, 2.5, 0.25) if isinstance(webobj, Driver) else WebDriverWait(webobj._parent)

class _By(RichEnumValue):
    pass

class By(Enum):
    """Enum for each of the finder method types"""
    CLASS = _By(canonical_name='class', display_name='by-class-name')
    CSS = _By(canonical_name='css_selector', display_name='by-css-selector')
    ID = _By(canonical_name='id', display_name='by-id')
    NAME = _By(canonical_name='name', display_name='by-name')
    TAG = _By(canonical_name='tag', display_name='by-tag-name')
    XPATH = _By(canonical_name='xpath', display_name='by-xpath')

def fclass(query: str, until: Wait = None):
    """Finds an element by class name
    
    Parameters:
    - `query`
        * A class name

    - `until`: optional
        * An optional wait condition to apply.

    Returns:
    - `Callable(WebObject)` :&#8658; `Response`
    """
    if not until:
        return responseof(lambda parent: Hit(parent.find_element_by_class_name(query)) if parent else Miss)
    else:
        return responseof(lambda parent: Hit(waitfor(parent).until(until(parent.find_element_by_class_name(query)))) if parent else Miss)

def fcss(query: str, until: Wait = None):
    """Finds an element by css selector
    
    Parameters:
    - `query`
        * A css selector string

    - `until`: optional
        * An optional wait condition to apply.

    Returns:
    - `Callable(WebObject)` :&#8658; `Response`
    """
    if not until:
        return responseof(lambda parent: Hit(parent.find_element_by_css_selector(query)) if parent else Miss)
    else:
        return responseof(lambda parent: Hit(waitfor(parent).until(until(parent.find_element_by_css_selector(query)))) if parent else Miss)

def fid(query: str, until: Wait = None):
    """Finds an element by id
    
    Parameters:
    - `query`
        * An id

    - `until`: optional
        * An optional wait condition to apply.

    Returns:
    - `Callable(WebObject)` :&#8658; `Response`
    """
    if not until:
        return responseof(lambda parent: Hit(parent.find_element_by_id(query)) if parent else Miss)
    else:
        return responseof(lambda parent: Hit(waitfor(parent).until(until(parent.find_element_by_id(query)))) if parent else Miss)

def fname(query: str, until: Wait = None):
    """Finds an element by name
    
    Parameters:
    - `query`
        * A name

    - `until`: optional
        * An optional wait condition to apply.

    Returns:
    - `Callable(WebObject)` :&#8658; `Response`
    """
    if not until:
        return responseof(lambda parent: Hit(parent.find_element_by_name(query)) if parent else Miss)
    else:
        return responseof(lambda parent: Hit(waitfor(parent).until(until(parent.find_element_by_name(query)))) if parent else Miss)

def ftag(query: str, until: Wait = None):
    """Finds an element by tag name
    
    Parameters:
    - `query`
        * An `HTML` tag name

    - `until`: optional
        * An optional wait condition to apply.

    Returns:
    - `Callable(WebObject)` :&#8658; `Response`
    """
    if not until:
        return responseof(lambda parent: Hit(parent.find_element_by_tag_name(query)) if parent else Miss)
    else:
        return responseof(lambda parent: Hit(waitfor(parent).until(until(parent.find_element_by_tag_name(query)))) if parent else Miss)

def fxpath(query: str, until: Wait = None):
    """Finds an element by xpath
    
    Parameters:
    - `query`
        * An xpath string

    - `until`: optional
        * An optional wait condition to apply.

    Returns:
    - `Callable(WebObject)` :&#8658; `Response`
    """
    if not until:
        return responseof(lambda parent: Hit(parent.find_element_by_xpath(query)) if parent else Miss)
    else:
        return responseof(lambda parent: Hit(waitfor(parent).until(until(parent.find_element_by_xpath(query)))) if parent else Miss)

def fxclass(query: str, until: Wait = None):
    """Finds elements by class name
    
    Parameters:
    - `query`
        * A class name

    - `until`: optional
        * An optional wait condition to apply.

    Returns:
    - `Callable(WebObject)` :&#8658; `Response`
    """
    if not until:
        return responseof(lambda parent: HitList(parent.find_elements_by_class_name(query)) if parent else Miss)
    else:
        return responseof(lambda parent: HitList(waitfor(parent).until(until(parent.find_elements_by_class_name(query)))) if parent else Miss)

def fxcss(query: str, until: Wait = None):
    """Finds elements by css selector
    
    Parameters:
    - `query`
        * A css selector string

    - `until`: optional
        * An optional wait condition to apply.

    Returns:
    - `Callable(WebObject)` :&#8658; `Response`
    """
    if not until:
        return responseof(lambda parent: HitList(parent.find_elements_by_css_selector(query)) if parent else Miss)
    else:
        return responseof(lambda parent: HitList(waitfor(parent).until(until(parent.find_elements_by_css_selector(query)))) if parent else Miss)

def fxid(query: str, until: Wait = None):
    """Finds elements by id
    
    Parameters:
    `query`
        An id

    `until`: optional
        An optional wait condition to apply.

    Returns:
    - `Callable(WebObject)` :&#8658; `Response`
    """
    if not until:
        return responseof(lambda parent: HitList(parent.find_elements_by_id(query)) if parent else Miss)
    else:
        return responseof(lambda parent: HitList(waitfor(parent).until(until(parent.find_elements_by_id(query)))) if parent else Miss)

def fxname(query: str, until: Wait = None):
    """Finds elements by name
    
    Parameters:
    - `query`
        * A name

    - `until`: optional
        * An optional wait condition to apply.

    Returns:
    - `Callable(WebObject)` :&#8658; `Response`
    """
    if not until:
        return responseof(lambda parent: HitList(parent.find_elements_by_name(query)) if parent else Miss)
    else:
        return responseof(lambda parent: HitList(waitfor(parent).until(until(parent.find_elements_by_name(query)))) if parent else Miss)

def fxtag(query: str, until: Wait = None):
    """Finds elements by tag name
    
    Parameters:
    _ `query`
        * An `HTML` tag name

    _ `until`: optional
        * An optional wait condition to apply.

    Returns:
    - `Callable(WebObject)` :&#8658; `Response`
    """
    if not until:
        return responseof(lambda parent: HitList(parent.find_elements_by_tag_name(query)) if parent else Miss)
    else:
        return responseof(lambda parent: HitList(waitfor(parent).until(until(parent.find_elements_by_tag_name(query)))) if parent else Miss)

def fxxpath(query: str, until: Wait = None):
    """Finds elements by xpath
    
    Parameters:
    - `query`
        * An xpath string

    - `until`: optional
        * An optional wait condition to apply.

    Returns:
    - `Callable(WebObject)` :&#8658; `Response`
    """
    if not until:
        return responseof(lambda parent: HitList(parent.find_elements_by_xpath(query)) if parent else Miss)
    else:
        return responseof(lambda parent: HitList(waitfor(parent).until(until(parent.find_elements_by_xpath(query)))) if parent else Miss)

def find(query: str, by: By, parent: WebObject, until: Wait = None) -> Response:
    """General finder method for a single element

    Parameters:
    `query`
        A string to search using
    
    `by`
        What `query` represents

    `parent`
        A driver or element

    `until`: optional
        An optional wait condition to apply

    Returns:
    - `Hit`
        * If element is found
    - `Miss`
        * If it is not
    """    
    if by == By.CSS:
        return fcss(query, until)(parent)
    elif by == By.ID:
        return fid(query, until)(parent)
    elif by == By.XPATH:
        return fxpath(query, until)(parent)
    elif by == By.TAG:
        return ftag(query, until)(parent)
    elif by == By.NAME:
        return fname(query, until)(parent)
    elif by == By.CLASS:
        return fclass(query, until)(parent)
    else:
        raise UnearthtimeException(':[%r]: Unrecognized `By` flag.')

def findall(query: str, by: By, parent: WebObject, until: Wait = None) -> Response:
    """General finder method for a list of elements

    Parameters:
    - `query`
        * A string to search using
    
    - `by`
        * What `query` represents

    - `parent`
        * A driver or element

    - `until`: optional
        * An optional wait condition to apply

    Returns:
    - `HitList`
        * If element is found
    - `Miss`
        * If it is not
    """   
    if by == By.CSS:
        return fxcss(query, until)(parent)
    elif by == By.ID:
        return fxid(query, until)(parent)
    elif by == By.XPATH:
        return fxxpath(query, until)(parent)
    elif by == By.TAG:
        return fxtag(query, until)(parent)
    elif by == By.NAME:
        return fxname(query, until)(parent)
    elif by == By.CLASS:
        return fxclass(query, until)(parent)
    else:
        raise UnearthtimeException(':[%r]: Unrecognized `By` flag.')