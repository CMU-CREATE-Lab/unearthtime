from __future__ import annotations

from time import sleep
from typing import Union, Tuple, Iterable

from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement as Element

from .tool import Tool
from .._algae.deco import returnonexception
from ..earthtime import EarthTime
from ..explore.response import Hit, Miss


class DLSearchResult:

    def __init__(self, label: Union[Element, Hit], category_name: str, earthtime: EarthTime):

        if isinstance(label, Element):
            label = Hit(label)

        self.__category_name = category_name
        self.__checkbox = Hit(label.find_element_by_tag_name('input'))
        self.__earthtime = earthtime
        self.__label = label
        self.__title = label.text.strip()

    def __repr__(self):
        return f'{DLSearchResult.__name__} : [{self.__category_name} : {self.__title}'

    @property
    def category_name(self):
        return self.__category_name

    @property
    def label(self) -> Hit:
        return self.__label

    @property
    def title(self):
        return self.__title

    def select(self):
        if bool(self.__earthtime) and self.__checkbox.is_displayed():
            self.__checkbox.click()


class DLSearchResults(Tuple[DLSearchResult]):

    def __new__(cls, query: str = '', results: Iterable[DLSearchResult] = None):
        return tuple.__new__(cls, results) if results else tuple.__new__(cls)

    def __init__(self, query: str = '', results: Iterable[DLSearchResult] = None):
        self.__query = query

    def __repr__(self):
        if len(self) > 0:
            return f'{DLSearchResults.__name__} [ Query: "{self.__query}"\n\t%s\n' % '\n\t'.join(map(str, self))
        else:
            return f'{DLSearchResults.__name__} [ Query: "{self.__query}" ]'

    @property
    def query(self):
        return self.__query

    def select_all(self):
        for result in self:
            result.select()


class DLSearchEngine(Tool):

    def __init__(self, earthtime: EarthTime):
        super().__init__(earthtime)
        self.__clear = None
        self.__empty_results_msg = None
        self.__input = None

    def clear(self):
        if self._informed and bool(self._earthtime) and self.__clear.is_displayed():
            self.__clear.click()

    @returnonexception(None, ElementNotInteractableException)
    def inform(self) -> bool:
        if self._informed:
            return bool(self._earthtime)
        elif self.informable():
            library = self._earthtime.DataLibraryMenu
            search_input = self._earthtime.DataLibrarySearchInput
            menu = search_input is Miss

            if not search_input:
                library.click()
                search_input = self._earthtime.DataLibrarySearchInput

            if clear := self._earthtime.DataLibrarySearchClearButton:
                query = search_input.value.encode('utf-8')
                clear.click()
                search_input.send_keys('*****')
                self.__clear = clear
                self.__empty_results_msg = self._earthtime.DataLibraryEmptySearchResultsMessage
            else:
                query = ''
                search_input.send_keys('*****')
                self.__clear = self._earthtime.DataLibrarySearchClearButton
                self.__empty_results_msg = self._earthtime.DataLibraryEmptySearchResultsMessage

            self.__clear.click()

            if query:
                search_input.send_keys(query)

            if menu:
                library.click()

            self._informed = True

        return self._informed

    @returnonexception(DLSearchResults(), StaleElementReferenceException)
    def search(self, query: str, clear: bool = True) -> DLSearchResults:
        if self.inform():
            library = self._earthtime.DataLibraryMenu
            search_input = self._earthtime.DataLibrarySearchInput
            menu = search_input is Miss

            if not search_input:
                library.click()

            if clear and self.__clear.is_displayed():
                self.__clear.click()

            self.__input.send_keys(query)

            sleep(0.5)

            if self.__empty_results_msg.is_displayed():
                return DLSearchResults()

            categories = self._earthtime.DataLibrarySearchFoundCategories
            results = {}

            for i in range(len(categories) - 1):
                results[categories[i].text] = self._earthtime['DataLibrarySearchFoundLabelsBetween', categories[i].text, categories[i + 1].text]

            results[categories[-1].text] = self._earthtime['DataLibrarySearchFoundLabelsAfter', categories[-1].text]

            if menu:
                library.click()

            return DLSearchResults(query, [DLSearchResult(label, category, self._earthtime) for category, labels in results.items() for label in labels])
        else:
            return DLSearchResults()
