"""The earthtime module defines classes used to control EarthTime webpages.

This module defines two types of `EarthTime` objects, one the standard
way of controlling a page, i.e. `EarthTime` and the other which caches
queries pulled using bracket-notation, `CachedEarthTime`.

Attributes:
    - `DriverType` : `Driver`, `() -> Driver`
    - `ElementPredicate : `(Element) -> bool, ([Element,]) -> bool, (Hit) -> bool, (HitList) -> bool
    - `_Explore` : `str` = 'https://earthtime.org/explore'
    - `_ImplicitWait : `int` = 0
"""

from __future__ import annotations

from functools import lru_cache, singledispatchmethod as overloaded
from io import BytesIO
from time import sleep
from typing import Callable, Final, Iterable, Union

from PIL import Image
from cv2 import cvtColor, COLOR_BGR2RGB, COLOR_BGR2GRAY
from numpy import array
from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webdriver import WebElement as Element

from ._algae.exceptions import UnearthtimeException
from ._algae.strings import ismalformedurl, resolvequery
from ._algae.utils import isnullary, istrue, raiseif
from .explore.image import AspectRatio, Thumbnail
from .explore.image import DEFAULT_HEIGHT, DEFAULT_WIDTH
from .explore.library import Library
from .explore.locator import ForcedLocator
from .explore.query import By, find as ufind, find_all as ufind_all, WaitType
from .explore.response import Hit, HitList, Miss
from .timelapse import Timelapse

DriverType = Union[Driver, Callable[[], Driver]]
ElementPredicate = Callable[[Union[Element, Iterable[Element], Hit, HitList]], bool]

_Explore: Final[str] = 'https://earthtime.org/explore'
_ImplicitWait: Final[int] = 0


class EarthTime:
    """A load-on-command EarthTime page."""
    _EarthTimePage = '_EarthTimePage'
    __total_pages = 0

    def __init__(self, driver: DriverType, url: str = _Explore):
        """
        Parameters:
            - `driver` : `WebDriver`, `() -> Driver`
            - `url` : `str

        Raises:
            - `UnearthtimeException` :
                - `url` is not of the form 'https://earthtime.org/explore' or 'https://earthtime.org/stories/story_name'.
                - `driver` is already connected to an `EarthTime` object.
                - `driver` is not a nullary callable.
        """
        raiseif(
            ismalformedurl(url) or not ('earthtime.org/' in url and ('explore' in url or 'stories/' in url)),
            UnearthtimeException(':[%s]: Url is not an EarthTime page.' % url)
        )

        EarthTime.__verify_driver(driver)

        self.__driver = driver
        self.__url = url
        self.__running = False
        self.__timelapse = None
        self.__history = []

    def __bool__(self):
        return self.__running

    def __call__(self, javascript: str, *args):
        return self.__driver.execute_script(javascript, *args)

    def __contains__(self, key: str):
        return True if key in Library else resolvequery(key) in Library

    def __enter__(self):
        if not self.__running:
            self.load()

        return self

    def __exit__(self, exc, val, traceback):
        self.quit()

    def __getattr__(self, name: str):
        """
        Given what `name` represents, the attribute returned will either be the result of a
        `Locator`, an attribute of the `WebDriver` or `Timelapse` for this instance.
        """
        if name in Library or resolvequery(name) in Library:
            return self.pull(name)
        elif hasattr(self.__driver, name):
            return self.__driver.__getattribute__(name)
        else:
            return self.__timelapse.__getattr__(name)

    def __getitem__(self, key: Union[str, tuple]):
        return self.pull(key) if isinstance(key, str) else self.pull(*key)

    def __repr__(self):
        return '%s:[%s]' % (EarthTime.__name__, self.__url)

    @classmethod
    def explore(cls, driver: DriverType, url: str = _Explore, imp_wait: Union[float, int] = _ImplicitWait):
        """Instantiates and loads an `EarthTime` page.

        Parameters:
            - `driver` : `WebDriver`, `() -> Driver`
            - `url` : `str
            - `imp_wait` : `float`, `int` = 0
        """
        et = cls(driver, url)
        et.load(imp_wait)

        return et

    @property
    def driver(self) -> DriverType:
        """The `WebDriver` for this instance."""
        return self.__driver

    @property
    def history(self) -> list:
        """A list of the queries to the DOM."""
        return self.__history

    @property
    def is_running(self) -> bool:
        """Whether or not this page is actively running."""
        return self.__running

    @property
    def timelapse(self) -> Timelapse:
        """The `Timelapse` associated with this instance."""
        return self.__timelapse

    def execute(self, javascript: str, *args):
        """Executes a string a javascript

        Parameters:
            - `javascript` : `str`
            - `*args`
        """
        return self.__driver.execute_script(javascript, *args)

    def find(self, query: str, by: By = By.CSS, until: WaitType = None):
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

        return ufind(query, by, self.__driver, until)

    def find_all(self, query: str, by: By = By.CSS, until: WaitType = None):
        """General finder method for a list of elements.

        Parameters:
            - `query` : `str`
            - `by` : `By`
            - `parent` : `WebDriver`, `WebElement`
            - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

        Returns:
            - `Hit`, `HitList`, `Miss`
        """

        return ufind_all(query, by, self.__driver, until)

    def get_thumbnail(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT) -> Thumbnail:
        """Gets a thumbnail of the current view of the page.

        Parameters:
            - `width` : `int` = 640
            - `height` : `int` = 360

        Returns:
            - `Thumbnail`
        """

        if self.__running:
            dim = AspectRatio.resolve_dimensions(width, height)
            url = cv if (cv := self.getThumbnailOfCurrentView(dim.width, dim.height)) else self('return timelapse.getThumbnailOfView(this, %d, %d)' % (dim.width, dim.height))

            return Thumbnail(url, dim)

    def goto(self, url: str):
        """Navigates driver to an EarthTime page.

        Parameters:
            - `url` : `str`

        Raises:
            - `UnearthtimeException` : `url` is not of the form 'https://earthtime.org/explore' or 'https://earthtime.org/stories/story_name'.
        """

        raiseif(
            ismalformedurl(url) or not ('earthtime.org/' in url and ('explore' in url or 'stories/' in url)),
            UnearthtimeException(':[%s]: Url is not an EarthTime page.' % url)
        )

        self.__driver.get(url)
        sleep(2.5)

    @overloaded
    def pull(self, key: Union[str, tuple], forced: bool = False):
        """Attempts to retrieve an element or elements using the provided `Locator` name and arguments.

        Parameters:
            - `key` : `str`, `tuple`
            - `forced` : `bool` = `False`

        Notes:

            - To override the wait condition associated with a `Locator` if one is, or simply provide one,
            it should be provided as the last argument of the tuple.
        """
        self.__history.append(key) if not forced else self.__history.append((key, True))
        return Miss

    @pull.register
    def _(self, key: str, forced: bool = False):
        self.__history.append(key) if not forced else self.__history.append((key, True))

        query = key if key in Library else (rkey if (rkey := resolvequery(key)) in Library else '')
        locator = Library[query] if not forced else ForcedLocator.from_locator(Library[query])

        return locator(self.__driver) if query else Miss

    @pull.register
    def _(self, key: tuple, forced: bool = False):
        name = key[0]
        if isinstance(name, str):
            if len(key) == 1:
                return self.pull(name, forced)

            self.__history.append(key) if not forced else self.__history.append(key + (True,))

            query = name if name in Library else (rname if (rname := resolvequery(name)) in Library else '')

            if query:
                locator = Library[query] if not forced else ForcedLocator.from_locator(Library[query])

                return locator(self.__driver, *key[1:]) if not callable(key[-1]) else locator(self.__driver, *key[1:-1], until=key[-1])

    def load(self, imp_wait: Union[float, int] = _ImplicitWait):
        """Instantiates the `WebDriver` of this instance and loads the page of the given `url`.

        Parameters:
            - `imp_wait` : `float`, `int` = 0

        Raises:
            - `UnearthtimeException` : The `WebDriver` for this instance is already connected to an `EarthTime` object.
        """
        if not self.__running:
            if callable(self.__driver):
                self.__driver = self.__driver()

                raiseif(
                    self.__driver._EarthTimePage is not None,
                    UnearthtimeException('Driver is already controlling an EarthTime page.')
                )

            self.__driver._EarthTimePage = self
            self.__driver.get(self.__url)

            sleep(5)

            self.__driver.maximize_window()

            if imp_wait > 0:
                self.__driver.implicitly_wait(imp_wait)

            self.__timelapse = Timelapse(self.__driver)
            self.__running = True
            self.__total_pages += 1

    def pause_at_end(self):
        """Pauses the timeline and sets it to the end."""
        self.__driver.execute_script('timelapse.pause(); timelapse.seek(%d)' % len(self.getCaptureTimes() - 1))

    def pause_at_start(self):
        """Pauses the timeline and sets it to the beginning."""
        self.__driver.execute_script('timelapse.pause(); timelapse.seek(0)')

    def quit(self):
        """Closes the page and quits the `WebDriver` of this instance."""
        if self.__running:
            self.__driver._EarthTimePage = None
            self.__url = ''
            self.__running = False
            self.__driver.quit()
            self.__driver = None
            EarthTime.__reset_driver()

    def release_driver(self) -> Driver:
        """Closes the page and returns the `WebDriver of this instance.

        Returns:
            - `WebDriver`
        """
        if self.__running:
            self.__driver._EarthTimePage = None
            self.__url = ''
            self.__running = False
            driver = self.__driver
            self.__driver = None
            EarthTime.__reset_driver()

            return driver

    def retry(self, index: int = -1):
        """Retries the query at a given index of the history.

        Parameters:
            `index` : int = -1

        Returns:
            - `Hit`, `HitList`, `Miss`
        """
        return self.pull(self.__history[index]) if -len(self.__history) <= index < len(self.__history) else Miss

    def retry_only_if(self, key: Union[str, tuple], condition: Union[bool, ElementPredicate], actions: Callable[[], None] = None):
        """Attempts to retrieve an element based on a given `Locator` name, retrying if it fails the `condition`.

        Parameters:
            - `key` : `str`, `tuple`
            - `condition` : `bool`, `(Element)` -> `bool`, `([Element,])` -> `bool`, `(Hit)` -> `bool`, `(HitList)` -> `bool`
            - `actions` : `()` -> `None` = `None`

        Returns:
            - `Hit`, `HitList`, `Miss`
        """
        res = self.pull(key)

        if condition is not None:
            if callable(condition) and istrue(condition(res)) and actions is not None:
                actions()
                return self.pull(key)
            elif istrue(condition) and actions is not None:
                actions()
                return self.pull(key)

        return res

    def screenshot(self, mode: str = 'png'):
        """Screenshots the window

        Parameters:
            - `mode` : `str` = 'png'

        Notes:
            - Valid modes are:
                - png, PNG
                - base64
                - img, IMG, image
                - array, ndarray
                - rgb, RGB
                - gray, grey

            - If 'png'/'PNG' is used the screenshot will colored using a BGR model. Use 'rgb'/'RGB' mode if this not desired.
        """

        if mode in ('png', 'PNG'):
            return self.__driver.get_screenshot_as_png()
        elif mode == 'base64':
            return self.__driver.get_screenshot_as_base64()
        elif mode in ('img', 'IMG', 'image'):
            return Image.open(BytesIO(self.__driver.get_screenshot_as_png()))
        elif mode in ('array', 'ndarray'):
            return array(Image.open(BytesIO(self.__driver.get_screenshot_as_png())))
        elif mode in ('rgb', 'RGB'):
            return cvtColor(array(Image.open(BytesIO(self.__driver.get_screenshot_as_png()))), COLOR_BGR2RGB)
        elif mode in ('gray', 'grey'):
            return cvtColor(array(Image.open(BytesIO(self.__driver.get_screenshot_as_png()))), COLOR_BGR2GRAY)

    def screenshot_and_save(self, path: str):
        """Screenshots the window and saves it as a '.png'

        Parameters:
            - `path` : `str`
        """
        self.__driver.get_screenshot_as_file(path)

    @staticmethod
    def __reset_driver():
        EarthTime.__total_pages -= 1

        if EarthTime.__total_pages == 0:
            del Driver._EarthTimePage

    @staticmethod
    def __verify_driver(driver: DriverType):
        raiseif(
            not (isinstance(driver, Driver) or (callable(driver) and isnullary(driver))),
            TypeError(':[%r]: Invalid driver.' % driver)
        )

        raiseif(
            isinstance(driver, Driver) and
            hasattr(driver, EarthTime._EarthTimePage) and
            driver._EarthTimePage is not None,
            UnearthtimeException('Driver is already controlling an EarthTime page.')
        )

        if not hasattr(Driver, EarthTime._EarthTimePage):
            Driver._EarthTimePage = None


class CachedEarthTime(EarthTime):
    """A load-on-command EarthTime page with cached index-access of predefined `Locators`."""

    @lru_cache
    def __getitem__(self, key: Union[str, tuple]): return self.pull(key)