"""The locator module defines classes for defining repeatable queries to the DOM.

The difference between a `Locator` and a `ForcedLocator` is that a `Locator` will
only return a `Hit` if the element is displayed. `ForcedLocator` returns a response
according to what is returned from the DOM, whether the element is displayed or not.

Examples:
        Assumes `driver` is already defined, and loaded to 'https://earthtime.org/explore'.

        ```
        >>> from unearthtime.explore.locator import Locator, ForcedLocator
        >>>
        >>> logo = Locator('menu-logo', By.ID)
        >>> logo
        Locator[Term: menu-logo, By: ID] -> Hit
        >>>
        >>> logo(driver)
        Hit[a1bd9191-86d3-471d-8bb6-a9e4c57b3a80]
        >>>
        >>> category_id = 'category-biodiversity'
        >>> category_header = Locator(lambda ac: "h3[aria-controls=%s]" % ac)
        >>>
        >>> category_header(driver, category_id)
        Miss
        >>>
        >>> forced_category_header = ForcedLocator.from_locator(category_header)
        >>>
        >>> forced_category_header(driver, category_id)
        Hit[67c23942-f825-42b7-9b40-f4f64d2b1a9e]
        ```
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Union

from .query import By, find, find_all, ResponseType, WaitType, WebObject
from .response import Hit, HitList, Miss
from .._algae.exceptions import UnearthtimeException
from .._algae.utils import is_nonstring_iterable, raiseif, where
from .._algae.warnings import overridinguseof

__all__ = ['ForcedLocator', 'Locator']


@dataclass
class Locator:
    """A 'self-aware' element locator.

    Given a successful response from the DOM, the element is only returned
    if it is displayed.

    Attributes:
        - `terms` : `str`, `Callable`, `Iterable[`str`, `Callable`]
        - `by` : `By`, `Iterable[By]` = `By.CSS`
        - `list_` : `bool` = `False`
        - `until` : `WaitType` = `None`
    """
    terms: Union[str, Callable, Iterable[Union[str, Callable]]]
    by: Union[By, Iterable[By]] = By.CSS
    list_: bool = False
    until: WaitType = None

    def __call__(self, parent: WebObject, *args, until: WaitType = None, **kwargs) -> ResponseType:
        """Sends a request to the DOM.

        Parameters:
            - `parent` : `WebDriver`, `WebElement`
            - `*args`
            - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = None
            - `**kwargs`

        Returns:
            - `Hit`
            - `HitList`
            - `Miss`

        Raises:
            - `UnearthtimeException` :
                - Arguments are passed in without any callable locators.
                - No arguments are passed in for callable locators.
                - Invalid `parent`.
        """

        raiseif(
            (bool(args) or bool(kwargs) and not (
                    callable(self.terms) or
                    (is_nonstring_iterable(self.terms) and any(map(callable, self.terms)))
            )),
            UnearthtimeException('Locator does not have any callable terms.')
        )

        raiseif(
            not (bool(args) or bool(kwargs)) and (
                    callable(self.terms) or
                    (is_nonstring_iterable(self.terms) and any(map(callable, self.terms)))
            ),
            UnearthtimeException('No arguments provided for callable term(s).')
        )

        raiseif(
            parent is None,
            UnearthtimeException('No driver or element provided to locate element.')
        )

        if until and self.until:
            overridinguseof(self.until, until)
        else:
            until = self.until

        if is_nonstring_iterable(self.terms):
            if isinstance(self.by, Iterable):
                raiseif(
                    len(self.terms) != len(self.by),
                    UnearthtimeException('Insufficient term-by pairs.')
                )
                bys = self.by
            else:
                bys = [self.by] * len(self.terms)

            for term, by in zip(self.terms, bys):
                query = term(*args, **kwargs) if callable(term) else term

                if self.list_:
                    if (hits := find_all(query, by, parent, until)) and where(lambda h: h.is_displayed(), hits):
                        return hits
                elif (hit := find(query, by, parent, until)) and hit.is_displayed():
                    return hit
            else:
                return Miss
        else:
            query = self.terms(*args, **kwargs) if callable(self.terms) else self.terms

            if self.list_:
                if (hits := find_all(query, self.by, parent, until)) and where(lambda h: h.is_displayed(), hits):
                    return hits
            elif (hit := find(query, self.by, parent, until)) and hit.is_displayed():
                return hit
            else:
                return Miss

    def __repr__(self):
        if is_nonstring_iterable(self.terms):
            if isinstance(self.by, Iterable):
                raiseif(
                    len(self.terms) != len(self.by),
                    UnearthtimeException('Insufficient term-by pairs.')
                )
                bys = self.by
            else:
                bys = [self.by] * len(self.terms)

            return "[\n\t%s\n]" % '\n\t'.join(
                ["%s[Term: %s, By: %s] \u2192 %s" % (
                    Locator.__name__,
                    term,
                    by.value.display_name.lstrip('by-').replace('-', ' ').upper(),
                    HitList.__name__ if self.list_ else Hit.__name__) for term, by in zip(self.terms, bys)])

        else:
            return "%s[Term: %s, By: %s] \u2192 %s" % (
                Locator.__name__,
                self.terms,
                self.by.value.display_name.lstrip('by-').replace('-', ' ').upper(),
                HitList.__name__ if self.list_ else Hit.__name__)


class ForcedLocator(Locator):
    """A 'self-aware' element locator.

    This locator does not check whether an element is displayed
    given a successful query to the DOM.

    Attributes:
        - `terms` : `str`, `Callable`, `Iterable[`str`, `Callable`]
        - `by` : `By`, `Iterable[By]` = `By.CSS`
        - `list_` : `bool` = `False`
        - `until` : `WaitType` = `None`
    """

    @classmethod
    def from_locator(cls, locator: Locator):
        return cls(locator.terms, locator.by, locator.list_, locator.until)

    def __call__(self, parent: WebObject, *args, until: WaitType = None, **kwargs) -> ResponseType:
        """Sends a request to the DOM.

        Parameters:
            - `parent` : `WebDriver`, `WebElement`
            - `*args`
            - `until` : `(WebDriver)` -> `Hit`, `HitList`, `False` = None
            - `**kwargs`

        Returns:
            - `Hit`
            - `HitList`
            - `Miss`

        Raises:
            - `UnearthtimeException` :
                - Arguments are passed in without any callable locators.
                - No arguments are passed in for callable locators.
                - Invalid `parent`.
        """

        raiseif(
            (bool(args) or bool(kwargs) and not (
                    callable(self.terms) or
                    (is_nonstring_iterable(self.terms) and any(map(callable, self.terms)))
            )),
            UnearthtimeException('Locator does not have any callable terms.')
        )

        raiseif(
            not (bool(args) or bool(kwargs)) and (
                    callable(self.terms) or
                    (is_nonstring_iterable(self.terms) and any(map(callable, self.terms)))
            ),
            UnearthtimeException('No arguments provided for callable term(s).')
        )

        raiseif(
            parent is None,
            UnearthtimeException('No driver or element provided to locate element.')
        )

        if until and self.until:
            overridinguseof(self.until, until)
        else:
            until = self.until

        if is_nonstring_iterable(self.terms):
            if isinstance(self.by, Iterable):
                raiseif(
                    len(self.terms) != len(self.by),
                    UnearthtimeException('Insufficient term-by pairs.')
                )
                bys = self.by
            else:
                bys = [self.by] * len(self.terms)

            for term, by in zip(self.terms, bys):
                query = term(*args, **kwargs) if callable(term) else term

                if self.list_:
                    if hits := find_all(query, by, parent, until):
                        return hits
                elif hit := find(query, by, parent, until):
                    return hit
            else:
                return Miss
        else:
            query = self.terms(*args, **kwargs) if callable(self.terms) else self.terms

            if self.list_:
                return find_all(query, self.by, parent, until)
            else:
                return find(query, self.by, parent, until)

    def __repr__(self):
        if is_nonstring_iterable(self.terms):
            if isinstance(self.by, Iterable):
                raiseif(
                    len(self.terms) != len(self.by),
                    UnearthtimeException('Insufficient term-by pairs.')
                )
                bys = self.by
            else:
                bys = [self.by] * len(self.terms)

            return "[\n\t%s\n]" % '\n\t'.join(
                ["%s[Term: %s, By: %s] \u2192 %s" % (
                    ForcedLocator.__name__,
                    term,
                    by.value.display_name.lstrip('by-').replace('-', ' ').upper(),
                    HitList.__name__ if self.list_ else Hit.__name__) for term, by in zip(self.terms, bys)])

        else:
            return "%s[Term: %s, By: %s] \u2192 %s" % (
                ForcedLocator.__name__,
                self.terms,
                self.by.value.display_name.lstrip('by-').replace('-', ' ').upper(),
                HitList.__name__ if self.list_ else Hit.__name__)
