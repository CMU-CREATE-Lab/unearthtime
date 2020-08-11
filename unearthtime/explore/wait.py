"""The wait module defines a simple way of creating custom explicit `WebDriver` waits.

Waits created using the provided class are more compatible with the Unearthtime framework,
than the Selenium method shown [here](https://selenium-python.readthedocs.io/waits.html),
under 'Custom Wait Conditions'. The 'locator' described in the link is NOT the same as the
locator defined in this framework, though they have similar purposes.
"""

from typing import Callable, Union

from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webelement import WebElement as Element

from .locator import Locator
from .response import Hit
from .._algae.utils import istrue


class Wait:
    """Represents a custom wait.

    Custom waits created this way functions differently than the `until` arguments
    passed into `Locator`s and the `find` and `find_all` methods, in that, a `Locator`
    itself can be used to initialize a custom `Wait`, where the `until` argument expects
    a `Callable` class initialized with an `WebElement` or `Hit`. However, if a custom wait
    is expected to be intialized with an `WebElement` or `Hit`, then it can be passed as
    the `until` argument.

    To use a custom wait initialized with a `Locator` we can either import the `wait_for`
    method from the `query` module, or using Selenium's `WebDriverWait` class imported from
    `selenium.webdriver.support.ui`.

    Selenium also provides some predefined expected conditions that follow the same rules,
    i.e. if the condition is initialized with a `WebElement` it can be passed to the `until`
    argument, otherwise the `wait_for` method or `WebDriverWait` class should be used.

    Examples:

        Assumes `driver` is defined and loaded to 'https://earthtime.org/stories/sahel_in_peril'

        ```
        >>> from unearthtime.explore.locator import ForcedLocator
        >>> from unearthtime.explore.query import wait_for
        >>> from unearthtime.explore.wait import Wait
        >>> from selenium.webdriver.support.ui import WebDriverWait
        >>> from selenium.webdriver.support import expected_conditions as EC
        >>>
        >>> legend = ForcedLocator('layers-legend', By.ID)
        >>>
        >>> wait_condition = Wait(legend, lambda element: element.is_displayed())
        >>>
        >>> legend(driver)
        Hit[7099af01-2a98-44f9-8a14-c93fcf762111]
        >>>
        >>> wait_for(driver).until(wait_condition)
        Miss
        >>>
        >>> WebDriverWait(driver).until(wait_condition)
        Miss
        >>>
        >>> legend(driver, until=EC.visibility_of)
        ```
    """

    def __init__(self, locator: Union[Element, Hit, Locator], condition: Callable[[Union[Element, Hit]], bool], *args, **kwargs):
        self.__locator = locator
        self.__args = args
        self.__kwargs = kwargs
        self.__condition = condition

    def __call__(self, driver: Driver):
        element = self.__locator(driver, *self.__args, **self.__kwargs) if isinstance(self.__locator, Locator) else self.__locator

        return istrue(self.__condition(element))
