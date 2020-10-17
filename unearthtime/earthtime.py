"""The earthtime module defines classes used to control EarthTime webpages.

This module defines two types of `EarthTime` objects, one the standard
way of controlling a page, i.e. `EarthTime` and the other which caches
queries pulled using bracket-notation, `CachedEarthTime`.

Attributes:
    - `DriverType`: `Driver`, `() -> Driver`
    - `ElementPredicate : `(Element) -> bool, ([Element,]) -> bool, (Hit) -> bool, (HitList) -> bool
    - `_Explore`: `str` = 'https://earthtime.org/explore'
    - `_ImplicitWait : `int` = 0
"""

from __future__ import annotations

import time
from functools import lru_cache, singledispatchmethod as overloaded
from queue import Queue
from typing import Callable, Final, Iterable, Union

from selenium.common.exceptions import InvalidSessionIdException
from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webdriver import WebElement as Element

from ._algae.exceptions import UnearthtimeException
from ._algae.strings import ismalformedurl, resolvequery
from ._algae.utils import isnullary, istrue, raiseif
from .explore.library import Library
from .explore.locator import ForcedLocator
from .explore.query import By, find as ufind, find_all as ufind_all, WaitType
from .explore.registry import Registry
from .explore.response import Hit, HitList, Miss
from .imaging.image import DEFAULT_HEIGHT, DEFAULT_WIDTH
from .imaging.image import Image, AspectRatio, Thumbnail
from .timelapse import Timelapse

DriverType = Union[Driver, Callable[[], Driver]]
ElementPredicate = Callable[[Union[Element, Iterable[Element], Hit, HitList]], bool]

_Explore: Final[str] = 'https://earthtime.org/explore'
_ImplicitWait: Final[int] = 0
_LoadedWait = 0.5


class EarthTime:
    """A load-on-command EarthTime page."""
    _EarthTimePage = '_EarthTimePage'
    __total_pages = 0

    def __init__(self, driver: DriverType, url: str = _Explore):
        """
        Parameters:
            - `driver`: `WebDriver`, `() -> Driver`
            - `url`: `str

        Raises:
            - `UnearthtimeException`:
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
        self.__registry = Registry(Library.StandardLocators)

    def __bool__(self):
        return self.__running

    def __call__(self, javascript: str, *args):
        return self.__driver.execute_script(javascript, *args)

    def __contains__(self, key: str):
        return True if key in self.__registry else resolvequery(key) in self.__registry

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
        if name in self.__registry or resolvequery(name) in self.__registry:
            return self.pull(name)
        elif hasattr(self.__driver, name):
            return self.__driver.__getattribute__(name)
        else:
            return self.__timelapse.__getattr__(name)

    def __getitem__(self, key: Union[str, tuple]):
        return self.pull(key) if not (isinstance(key, tuple) and isinstance(key[-1], bool)) else self.pull(key[:-1], key[-1])

    def __repr__(self):
        return '%s:[%s]' % (EarthTime.__name__, self.__url)

    @classmethod
    def explore(cls, driver: DriverType, url: str = _Explore, load_wait: Union[float, int] = 0, imp_wait: Union[float, int] = _ImplicitWait):
        """Instantiates and loads an `EarthTime` page.

        Parameters:
            - `driver`: `WebDriver`, `() -> Driver`
            - `url`: `str`
            - `load_wait`: `float`, `int` = 0
            - `imp_wait`: `float`, `int` = 0
        """
        et = cls(driver, url)
        et.load(load_wait, imp_wait)

        return et

    @classmethod
    def explore_from_hash(cls, driver: DriverType, hash_: str, root_url: str = _Explore, load_wait: Union[float, int] = 0, imp_wait: Union[float, int] = _ImplicitWait):
        """Instantiates and loads an `EarthTime` page from a hash.

        Parameters:
            - `driver`: `WebDriver`, `() -> Driver`
            - `hash_`: `str`
            - `load_wait`: `float`, `int` = 0
            - `imp_wait`: `float`, `int` = 0

        Notes:
            - `hash_` should not have a '#' in front of it. The `url` will be rendered as `root_url#hash_to_layer_or_waypoint`
        """
        et = cls(driver, f'{root_url}#{hash_}')
        et.load(load_wait, imp_wait)

        return et

    @classmethod
    def from_hash(cls, driver: DriverType, hash_: str, root_url: str = _Explore):
        """Instantiates an `EarthTime` page from a hash.

        Parameters:
            - `driver`: `WebDriver`, `() -> Driver`
            - `hash_`: `str`
            - `root_url`: `str`

        Notes:
            - `hash_` should not have a '#' in front of it. The `url` will be rendered as `root_url#hash_to_layer_or_waypoint`
        """
        return cls(driver, f'{root_url}#{hash_}')

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
    def registry(self) -> Registry:
        return self.__registry

    @property
    def timelapse(self) -> Timelapse:
        """The `Timelapse` associated with this instance."""
        return self.__timelapse

    def execute(self, javascript: str, *args):
        """Executes a string a javascript

        Parameters:
            - `javascript`: `str`
            - `*args`
        """
        return self.__driver.execute_script(javascript, *args)

    def find(self, query: str, by: By = By.CSS, until: WaitType = None):
        """General finder method for a single element.

        Parameters:
            - `query`: `str`
            - `by`: `By`
            - `parent`: `WebDriver`, `WebElement`
            - `until`: `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

        Returns:
            - `Hit`, `HitList`, `Miss`

        Raises:
            - `UnearthtimeException`: Invalid `by` enum.
        """

        return ufind(query, by, self.__driver, until)

    def find_all(self, query: str, by: By = By.CSS, until: WaitType = None):
        """General finder method for a list of elements.

        Parameters:
            - `query`: `str`
            - `by`: `By`
            - `parent`: `WebDriver`, `WebElement`
            - `until`: `(WebDriver)` -> `Hit`, `HitList`, `False` = `None`

        Returns:
            - `Hit`, `HitList`, `Miss`
        """

        return ufind_all(query, by, self.__driver, until)

    def get_thumbnail(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT) -> Thumbnail:
        """Gets a thumbnail of the current view of the page.

        Parameters:
            - `width`: `int` = 640
            - `height`: `int` = 360

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
            - `url`: `str`

        Raises:
            - `UnearthtimeException`: `url` is not of the form 'https://earthtime.org/explore' or 'https://earthtime.org/stories/story_name'.
        """

        raiseif(
            ismalformedurl(url) or not ('earthtime.org/' in url and ('explore' in url or 'stories/' in url)),
            UnearthtimeException(':[%s]: Url is not an EarthTime page.' % url)
        )

        self.__driver.get(url)
        time.sleep(2.5)

    def hide_extras(self):
        """Hides the container with extras content if it is visible."""
        if (cnt := self.ExtrasContentContainer) and cnt.is_visible:
            if btn := self.ExtrasContentContainerButton:
                btn.click()
            else:
                self('arguments[0].hide()', cnt._element)

    @overloaded
    def pull(self, key: Union[str, tuple], forced: bool = False):
        """Attempts to retrieve an element or elements using the provided `Locator` name and arguments.

        Parameters:
            - `key`: `str`, `tuple`
            - `forced`: `bool` = `False`

        Notes:

            - To override the wait condition associated with a `Locator` if one is, or simply provide one,
            it should be provided as the last argument of the tuple.
        """
        self.__history.append(key) if not forced else self.__history.append((key, True))
        return Miss

    @pull.register
    def _(self, key: str, forced: bool = False):
        self.__history.append(key) if not forced else self.__history.append((key, True))

        query = key if key in self.__registry else (rkey if (rkey := resolvequery(key)) in self.__registry else '')
        locator = self.__registry[query] if not forced else ForcedLocator.from_locator(self.__registry[query])

        return locator(self.__driver) if query else Miss

    @pull.register
    def _(self, key: tuple, forced: bool = False):
        name = key[0]
        if isinstance(name, str):
            if len(key) == 1:
                return self.pull(name, forced)

            self.__history.append(key) if not forced else self.__history.append(key + (True,))

            query = name if name in self.__registry else (rname if (rname := resolvequery(name)) in self.__registry else '')

            if query:
                locator = self.__registry[query] if not forced else ForcedLocator.from_locator(self.__registry[query])

                return locator(self.__driver, *key[1:]) if not callable(key[-1]) else locator(self.__driver, *key[1:-1], until=key[-1])

    def load(self, load_wait: Union[float, int] = 0, imp_wait: Union[float, int] = _ImplicitWait):
        """Instantiates the `WebDriver` of this instance and loads the page of the given `url`.

        Parameters:
            - `load_wait`: `float`, `int` = 0
            - `imp_wait`: `float`, `int` = 0

        Raises:
            - `UnearthtimeException`: The `WebDriver` for this instance is already connected to an `EarthTime` object.
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

            time.sleep(1)

            self.__driver.maximize_window()

            if load_wait > 0:
                time.sleep(load_wait)

            if imp_wait > 0:
                self.__driver.implicitly_wait(imp_wait)

            self.__timelapse = Timelapse(self.__driver)
            self.__running = True
            self.__total_pages += 1

    def map_loaded(self, draw_calls: int = 0, wait: Union[float, int] = _LoadedWait) -> bool:
        """Whether or not the last frame has been completely drawn for a layer.

        Parameters:
            * `draw_calls`: int = 0
        """
        if draw_calls > 0:
            calls = 0

            while self.isSpinnerShowing():
                pass

            wait = (wait + abs(wait)) / 2

            while not self.lastFrameCompletelyDrawn and calls < draw_calls:
                time.sleep(wait)
                calls += 1

        return self.lastFrameCompletelyDrawn

    def new_session(self, url: str = _Explore):
        """Starts a new driver session, a page loaded with the given url.

        Parameters:
            * `url`: str = 'https://earthtime.org/explore'
        """

        raiseif(
            ismalformedurl(url) or not ('earthtime.org/' in url and ('explore' in url or 'stories/' in url)),
            UnearthtimeException(':[%s]: Url is not an EarthTime page.' % url)
        )

        self.__driver.start_session({})
        self.__driver.get(url)

        time.sleep(2)

        self.__driver.maximize_window()

    def pause_at_end(self):
        """Pauses the timeline and sets it to the end."""
        if self.TimelineControl and (btn := self.TimelinePlayPauseButton):
            if btn['title'] == 'Pause':
                btn.click()

            if not self.isPaused():
                self.__driver.execute_script('timelapse.pause();')

            self.__driver.execute_script(f'timelapse.seekToFrame({len(self.getCaptureTimes()) - 1});')

    def pause_at_middle(self):
        """Pauses the timeline and setis it to the middle.

        Notes:
            * The middle is defined by half the length of the total capture times rounded down.
        """
        if self.TimelineControl and (btn := self.TimelinePlayPauseButton):
            if btn['title'] == 'Pause':
                btn.click()

            if not self.isPaused():
                self.__driver.execute_script('timelapse.pause();')

            self.__driver.execute_script(f'timelapse.seekToFrame({len(self.getCaptureTimes()) // 2});')

    def pause_at_start(self):
        """Pauses the timeline and sets it to the beginning."""
        if self.TimelineControl and (btn := self.TimelinePlayPauseButton):
            if btn['title'] == 'Pause':
                btn.click()

            if not self.isPaused():
                self.__driver.execute_script('timelapse.pause();')

            self.__driver.execute_script('timelapse.seekToFrame(0);')

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
            `index`: int = -1

        Returns:
            - `Hit`, `HitList`, `Miss`
        """
        return self.pull(self.__history[index]) if -len(self.__history) <= index < len(self.__history) else Miss

    def retry_only_if(self, key: Union[str, tuple], condition: Union[bool, ElementPredicate], actions: Callable[[], None] = None):
        """Attempts to retrieve an element based on a given `Locator` name, retrying if it fails the `condition`.

        Parameters:
            - `key`: `str`, `tuple`
            - `condition`: `bool`, `(Element)` -> `bool`, `([Element,])` -> `bool`, `(Hit)` -> `bool`, `(HitList)` -> `bool`
            - `actions`: `()` -> `None` = `None`

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

    def screenshot(self, mode: str = 'RGB'):
        """Screenshots the window

        Parameters:
            - `mode`: `str` = 'png'

        Notes:
            - Valid modes are:
                - png, PNG
                - base64
                - img, IMG, image
                - color space
        """

        if mode in ('png', 'PNG'):
            return self.__driver.get_screenshot_as_png()
        elif mode == 'base64':
            return self.__driver.get_screenshot_as_base64()
        elif mode in ('img', 'IMG', 'image'):
            return Image.from_bytes(self.__driver.get_screenshot_as_png())
        elif mode in ('array', 'ndarray'):
            return Image.from_bytes(self.__driver.get_screenshot_as_png()).array()
        else:
            return Image.from_bytes(self.__driver.get_screenshot_as_png(), mode)
        
    def screenshot_and_save(self, fp: str = './', color_space: str = 'RGB', format_=None, **params):
        """Screenshots the window and saves it as a '.png'

        Parameters:
            - `fp`: `str` = './'
            - `color_space`: str = 'BGR'
            - `format` = None
            - `**params`
        """
        self.screenshot(color_space).save(fp, format_, **params)

    def screenshot_content(self, mode: str = 'RGB'):
        """Screenshots the data panes

        Parameters:
            - `mode`: `str` = 'png'

        Notes:
            - Valid modes are:
                - png, PNG
                - base64
                - img, IMG, image
                - color space
        """
        return self.DataPanes.screenshot(mode)
    
    def screenshot_content_and_save(self, fp: str = './', color_space: str = 'RGB', format_=None, **params):
        """Screenshots the data panes and saves it.

        Parameters:
            - `fp`: `str` = './'
            - `color_space`
            - `format`
            - `**params`
        """
        self.DataPanes.screenshot_and_save(fp, color_space, format_, **params)

    def set_hash(self, hash_: str, draw_calls: int = 0, wait: Union[float, int] = _LoadedWait):
        """Alters the url to include a hash."""
        self(f"window.location.hash = '{hash_}'")
        return self.map_loaded(draw_calls, wait)

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


class EarthTimePool:
    __instance = None

    def __new__(cls, driver: Callable[[], Driver], size: int = 5):
        if EarthTimePool.__instance is None:
            EarthTimePool.__instance = object.__new__(cls)

        return EarthTimePool.__instance

    def __init__(self, driver: Callable[[], Driver], size: int = -1):
        self.__available_count = 0
        self.__available = Queue(size) if size > 0 else Queue()
        self.__driver = driver
        self.__occupied = {}
        self.__size = size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    @property
    def available_instances(self):
        return self.__available_count

    @property
    def occupied_instances(self):
        return len(self.__occupied)

    @property
    def size(self):
        return self.__size

    def acquire(self, url: str = _Explore, load_wait: Union[float, int] = 0, imp_wait: Union[float, int] = _ImplicitWait, block: bool = True, timeout: float = None):
        if self.__available_count > 0:
            et = self.__available.get_nowait()

            if bool(et):
                try:
                    _ = et.window_handles
                except InvalidSessionIdException:
                    pass
                else:
                    self.__occupied[et.session_id] = et
                    self.__available_count -= 1
                    return self.acquire(url, load_wait, imp_wait, block, timeout)
            else:
                return self.acquire(url, load_wait, imp_wait, block, timeout)

            et.driver.start_session({})
            et.driver.get(url)

            time.sleep(2)

            et.driver.maximize_window()

            if load_wait > 0:
                time.sleep(load_wait)

            if imp_wait > 0:
                et.driver.implicitly_wait(imp_wait)

            self.__available_count -= 1

        elif self.__size > 0:

            if len(self.__occupied) < self.__size:
                et = EarthTime.explore(self.__driver, url, imp_wait)
            else:
                et = self.__available.get(block, timeout)

                et.driver.start_session({})
                et.driver.get(url)

                time.sleep(5)

                et.driver.maximize_window()

                if imp_wait > 0:
                    et.driver.implicitly_wait(imp_wait)

                self.__available_count -= 1
        else:
            et = EarthTime.explore(self.__driver, url, imp_wait)

        self.__occupied[et.session_id] = et

        return et

    def clean_up(self):
        to_delete = []

        for session_id, et in self.__occupied.items():
            if bool(et):
                try:
                    _ = et.window_handles
                except InvalidSessionIdException:
                    self.__available.put_nowait(et)
                    self.__available_count += 1

                    to_delete.append(session_id)
            else:
                to_delete.append(session_id)

        for session_id in to_delete:
            del self.__occupied[session_id]

    def quit(self):
        self.clean_up()

        for et in self.__occupied.values():
            et.quit()

        self.__occupied.clear()

        while not self.__available.empty():
            et = self.__available.get_nowait()

            if bool(et):
                et.quit()

    def release(self, session_id: str):
        raiseif(
            session_id not in self.__occupied,
            UnearthtimeException(f':[{session_id}]: EarthTime instance does not belong to pool.')
        )

        et = self.__occupied[session_id]

        if bool(et):
            et.close()
            self.__available.put_nowait(et)
