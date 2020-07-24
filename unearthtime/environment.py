from __future__ import annotations
from _algae.exceptions import UnearthtimeException
from _algae.strings import ismalformedurl, resolvequery
from _algae.typing import ElementPredicate
from _algae.utils import isnullary, isfalse, istrue, raiseif
from _algae.utils import newlambda

from cv2 import cvtColor, COLOR_BGR2RGB, COLOR_BGR2GRAY
from explore.image import AspectRatio, Thumbnail
from explore.image import DEFAULT_HEIGHT, DEFAULT_WIDTH
from explore.locators import Locators
from explore.query import By, find as qfind, findall as qfindall
from explore.response import Miss
from functools import lru_cache, partial
from functools import singledispatchmethod as overloaded
from io import BytesIO
from numpy import array
from PIL import Image
from queue import SimpleQueue
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webdriver import WebDriver as Driver
from threading import Lock
from timelapse import Timelapse
from typing import Callable, Union

DriverType = Union[Driver, Callable[[], Driver]]

_Driver = lambda: Chrome('drivers/chromedriver.exe')
_Explore = 'https://earthtime.org/explore'
_ImplicitWait = 0
_Missed = lambda e: e is Miss
    
class Environment:
    """
    An `Environment` is the standard way of controlling an EarthTime webpage. It provides the easiest means of accessing and handling of elements within the DOM.

    Their are two types of environments:

    - `Environment`

        * The main class that defines all the behavior
    
    - `CachedEnvironment`

        * The same as `Environment` but the index-access is cached
  """
    _UEEnv = '_UnearthtimeEnvironment'
    __envs = 0

    def __init__(self, url: str = _Explore, driver: DriverType = _Driver):
        """
        Parameters:
        - `url` : `str` = 'https://earthtime.org/explore'

            * An optional string of the form 'https://name.earthtime.org/explore' or 'https://name.earthtime.org/stories/story'
        
        - `driver`: `WebDriver`, `Callable()` &#8658; `WebDriver` = `lambda: selenium.webdriver.Chrome('drivers/chromedriver.exe')`

            * An optional Selenium `WebDriver` or a zero-arg function that returns a `WebDriver`

        Raises:  
        - `UnearthtimeException`

            * If `url` is malformed or not an accepted EarthTime page

            * If `driver` is associated with another `Environment`
         
        - `TypeError`
            * If `driver` is not of an accepted type
        """
        raiseif(
            ismalformedurl(url) or not ('earthtime.org/' in url and ('explore' in url or 'stories' in url)), 
            UnearthtimeException(':[%s]: Url is not an EarthTime site.' % url))

        self.__verify_driver(driver)

        self.__driver = driver
        self.__active = False
        self.__timelapse = None
        self.__url = url
        self.__history = []
        self._lock = Lock()
        Environment.__envs += 1

    def __bool__(self): return self.__active

    def __call__(self, javascript: str, *args): return self.execute(javascript, *args)

    def __contains__(self, key: str): return True if key in Locators else resolvequery(key) in Locators

    def __enter__(self):
        if not self.__active:
            self.activate()
        return self

    def __exit__(self, exc, val, traceback): self.quit()

    def __getattr__(self, name: str):
        """
        Depending on what `name` represents it will return the result of a `Locator` , a `WebDriver` attribute or whatever is represented by executing the javascript statement `return timelapse.[name]`
        
        If `name` represents a function in timelapse.js, it will be converted into a lambda expression accepting the same number of arguments.
        """
        if name in Locators or resolvequery(name) in Locators:
            return self.pull(name)
        elif hasattr(self.__driver, name):
            return self.driver.name
        else:
            return self.__timelapse.__getattr__(name)
        
        return self.pull(name)

    def __repr__(self): return 'Environment[for=(%r)]' % self.__driver

    def __getitem__(self, key: Union[str, tuple]): 
        """
        Attempts to retrieve an element or elements of the provided `Locator` name, caching the result of the query
        
        Parameters:
        - `key`: `str`, `tuple`
            * The name of a predefined `Locator` or a tuple containing the name and any arguments needed for its `Locator`(s) or their `term`(s)
            
            * To override the wait condition associated with a `Locator` if one is, or simply provide one, either the last or second-to-last if an index is provided element of the tuple must be a `Callable(WebDriver)` :&#8658; `Hit`, `HitList`, `False`
        
            * Optionally, the last argument can also be an `int` specifying which `Locator` to use in the cases when a name has several, e.g. `ThemeHeader` can be accessed either using it's *id* or *aria-controls* attribute
        """
        return self.pull(key)

    @classmethod
    def explore(cls, url: str = _Explore, driver: DriverType =_Driver, imp_wait: int = _ImplicitWait):
        """Activates the environment before returning it

        Parameters:
        - `url` : `str` = 'https://earthtime.org/explore'

            * An optional string of the form 'https://name.earthtime.org/explore' or 'https://name.earthtime.org/stories/story'
        
        - `driver`: `WebDriver`, `Callable()` &#8658; `WebDriver` = `lambda: selenium.webdriver.Chrome('drivers/chromedriver.exe')`

            * An optional Selenium `WebDriver` or a zero-arg function that returns a `WebDriver`
        """
        environment = cls(url, driver)
        environment.activate(imp_wait)

        return environment

    @property
    def driver(self): return self.__driver

    @property
    def timelapse(self): return self.__timelapse

    @property
    def history(self): return self.__history

    def activate(self, imp_wait: int = _ImplicitWait):
        """
        Instantiates the `WebDriver` of this environment if necessary, then loads the page associated with the given url. The page will be maximized automatically

        Parameters:
        - `imp_wait`: `int` = 0
         
            * An implicit wait time in seconds to be used by the driver every time it tries to access an element and fails. It tells the driver how long to poll the DOM when trying to find an element or elements. The `implicitly_wait` method can be used to change this value after activation.
        """
        if not self.__active:
            if callable(self.__driver):
                self.__driver = self.__driver()

                raiseif(self.__driver._UnearthtimeEnvironment is not None,
                    UnearthtimeException(':[%r]: Driver already has an environment.' % self.__driver))

            self.__driver._UnearthtimeEnvironment = self

            self.__driver.get(self.__url)
            self.__driver.maximize_window()

            if imp_wait > 0:
                self.__driver.implicitly_wait(imp_wait)

            self.__timelapse = Timelapse(self.__driver)
            self.__active = True

    def execute(self, javascript: str, *args): 
        """
        Executes a string of javascript with the provided arguments

        Parameters:
        - `javascript` : `str`
            * Semicolon separated javascript statements

        - `*args`
            * An optional list of arguments to be used when executing the statement(s). Arguments can appear in the `javascript` string using the form *'arguments[n]'*, where *'n'* is the zero-based index of the argument in the `*args` list
        """
        return self.__driver.execute_script(javascript, *args)

    def find(self, query: str, by: By = By.CSS, until: Wait = None ): 
        """
        Attempts locate an element in the DOM satisfying a query

        Parameters:
        - `query` : `str`
            * The string to search for

        - `by` : `By` = `By.CSS`
            * What `query` is supposed to represent

        - `until` : `Callable(WebDriver)` :&#8658; `Hit`, `HitList`, `False`
            * A wait condition to poll when trying to find the element
        """
        return qfind(query, by, self.__driver, until)

    def findall(self, query, by=By.CSS, until: Wait = None ): 
        """
        Attempts locate all elements in the DOM satisfying a query

        Parameters:
        - `query` : `str`
            * The string to search for
         
        - `by` : `By` = `By.CSS`
            * What `query` is supposed to represent
         
        - `until` : `Callable(WebDriver)` :&#8658; `Hit`, `HitList`, `False`
            * A wait condition to poll when trying to find the element
        """
        return qfindall(query, by, self.__driver, until)

    def goto(self, url: str):
        """Navigates to the given url.
        
        Parameters:
        - `url` : `str`
            * A URL
        """
        self.__driver.get(url)

    @overloaded
    def pull(self, key: Union[str, tuple]): 
        """
        Attempts to retrieve an element or elements of the provided `Locator` name

        Parameters:
        - `key`: `str`, `tuple`
            * The name of a predefined `Locator` or a tuple containing the name and any arguments needed for its `Locator`(s) or their `term`(s)

        Notes: 
         
         - To override the wait condition associated with a `Locator` if one is, or simply provide one, either the last or second-to-last if an index is provided element of the tuple must be a `Callable(WebDriver)` :&#8658; `Hit`, `HitList`, `False`
        
        - Optionally, the last argument can also be an `int` specifying which `Locator` to use in the cases when a name has several, e.g. `ThemeHeader` can be accessed either using it's *id* or *aria-controls* attribute
        """
        self.__history.append(key)
        return Miss

    @pull.register
    def _(self, key: str):
        self.__history.append(key)

        query = key if key in Locators else (rkey if (rkey := resolvequery(key)) in Locators else '')

        if query:

            locator = Locators[query]

            if isinstance(locator, tuple):
                element = locator[0](self.__driver)

                if not element:
                    for i in range(1, len(locator)):
                        element = locator[i](self.__driver)
                        if element:
                            break

                return element
            else:
                return locator(self.__driver)
        else:
            return Miss
    
    @pull.register
    def _(self, key: tuple):
        self.__history.append(key)

        if isinstance(key[0], str):

            if len(key) == 1:
                return self.pull(key[0])

            query = key[0] if key[0] in Locators else (rkey if (rkey := resolvequery(key[0])) in Locators else '')

            if query:

                    locator = Locators[query]

                    if isinstance(locator, tuple):
                        if isinstance(key[-1], int) and -len(locator) <= key[-1] < len(locator):
                            if callable(key[-2]):
                                element = locator[key[-1]](self.__driver, *key[1:-2], until=key[-2])
                            else:
                                element = locator[key[-1]](self.__driver, *key[1:-1])
                        elif callable(key[-1]):
                            element = locator[0](self.__driver, *key[1:-1], until=key[-1])

                            if not element:
                                for i in range(1, len(locator)):
                                    element = locator[i](self.__driver, *key[1:-1], until=key[-1])

                                    if element:
                                        break
                        else:
                            element = locator[0](self.__driver, *key[1:])

                            if not element:
                                for i in range(1, len(locator)):
                                    element = locator[i](self.__driver, *key[1:])

                                    if element:
                                        break

                        return element
                    else:
                        return locator(self.__driver, *key[1:]) if not callable(key[-1]) else locator(self.__driver, *key[1:-1], until=key[-1])

        return Miss

    def is_active(self) -> bool:
        """Whether or not the environment is still connected to a driver"""
        return self.__active

    def pause_at_start(self): 
        """Pauses the timeline and sets it to the beginning"""
        self.execute('timelapse.pause(); timelapse.seek(0);')

    def pause_at_end(self): 
        """Pauses the timeline and sets it to the end"""
        self.execute('timelapse.pause(); timelapse.seek(%s);' % str(len(self.getCaptureTimes() - 1)))
    
    def quit(self):
        """Deactivates the environment and quits the driver"""
        self.__driver._UnearthtimeEnvironment = None
        self.__url = ''
        self.__active = False
        self.__driver.quit()
        self.__driver = None
        self.__clean_up_env()

    def release_driver(self):
        """Deactivates the environment returning the running driver"""
        self.__driver._UnearthtimeEnvironment = None
        self.__url = ''
        self.__active = False
        
        driver = self.__driver
        self.__driver = None

        self.__clean_up_env()

        return driver

    def repeat(self, index: int = -1): return self.pull(self.__history[index]) if -len(self.__history) <= index < len(self.__history) else Miss

    def repeat_if(self, key: Union[str, tuple], condition: Union[bool, ElementPredicate] = _Missed, actions: Callable[[], None] = None):
        res = self.pull(key)

        if condition is None:
            if res is Miss:
                if actions:
                    actions()
                    return self.pull(key)
        elif callable(condition):
            if istrue(condition(res)):
                if actions:
                    actions()
                    return self.pull(key)
        elif istrue(condition):
            if actions:
                actions()
                return self.pull(key)
        
        return res

    def screenshot(self, mode: str = 'png'):
        """Takes a screenshot

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
            return self.__driver.get_screenshot_as_png()
        elif mode == 'base64':
            return self.__driver.get_screenshot_as_base64()
        elif mode == 'img':
            return Image.open(BytesIO(self.__driver.get_screenshot_as_png()))
        elif mode == 'array':
            return array(Image.open(BytesIO(self.__driver.get_screenshot_as_png())))
        elif mode == 'rgb':
            return cvtColor(array(Image.open(BytesIO(self.__driver.get_screenshot_as_png()))), COLOR_BGR2RGB)
        elif mode == 'gray' or mode == 'grey':
            return cvtColor(array(Image.open(BytesIO(self.__driver.get_screenshot_as_png()))), COLOR_BGR2GRAY)
            
    def screenshot_and_save(self, path: str):
        """Takes a screenshot and saves it

        Parameters:
        - `path`: `str`
            * The path to save the image to
        """
        self.__driver.get_screenshot_as_file(path)

    def thumbnail(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT) -> Thumbnail:
        """
        A thumbnail of the current view as defined by the methods `Timelapse.getThumbnailOfCurrentView` or `Timelapse.getThumbnailOfView`

        Parameters:
        - `width` : `int`, `float`, `AspectRatio`, `None` = `640`

            * The width of the thumbnail expressed directly or as a ratio width-to-height

        - `height` : `int`, `float`, `AspectRatio`, `None` = `320`

            * The height of the thumbnail expressed directly or as a ratio height-to-width
        """
        w, h = AspectRatio.resolve_dimensions(width, height)
        url = current_view if (current_view := self.execute('return timelapse.getThumbnailOfCurrentView(%d, %d);' % (w, h))) else self.execute('return timelapse.getThumbnailOfView(this, %d, %d);' % (w, h))

    def __clean_up_env(self):
        Environment.__envs -= 1

        if Environment.__envs == 0:
            del Driver._UnearthtimeEnvironment

    def __verify_driver(self, driver):
        raiseif(
            not(isinstance(driver, Driver) or
                (callable(driver) and isnullary(driver))),
            TypeError(':[%r]: Invalid driver.' % driver))

        raiseif(
            isinstance(driver, Driver) and
            hasattr(Driver, Environment._UEEnv) and
            driver._UnearthtimeEnvironment is not None,
            UnearthtimeException('Driver already has an environment.'))

        if not hasattr(Driver, Environment._UEEnv):
            Driver._UnearthtimeEnvironment = None

class CachedEnvironment(Environment):

    @lru_cache
    def __getitem__(self, key):
        return self.pull(key)


        