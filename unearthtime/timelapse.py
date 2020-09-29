"""The timelapse module defines a wrapper around `timelapse.js`"""
from functools import partial

from selenium.webdriver.remote.webdriver import WebDriver as Driver

from unearthtime._algae.utils import newlambda


class Timelapse:
    """Wrapper for `timelapse.js`.

    All attributes of `timelapse.js` can be accessed via dot-notation. If
    the attribute represents a function, it will be converted into a lambda
    expression.

    Examples:

        Assumes `driver` is defined and loaded to 'https://earthtime.org/explore'


    """

    def __init__(self, driver: Driver):
        self.__driver = driver

    def __getattr__(self, name: str):
        res = self.__driver.execute_script(f'return timelapse.{name}')

        if isinstance(res, dict) and len(res) == 0 and self.__driver.execute_script(f'return typeof(timelapse.{name})') == 'function':
            length = self.__driver.execute_script(f'return timelapse.{name}.length')
            func = {}

            exec(newlambda('timelapse', name, length), func)

            return partial(func['f'], self.__driver)
        else:
            return res
