from __future__ import annotations

from collections import namedtuple
from time import sleep
from timeit import default_timer as timer
from typing import Union

from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement as Element

from .tool import SelectableTool
from .._algae.deco import returnonexception
from .._algae.exceptions import UnearthtimeException
from .._algae.strings import noneorempty
from .._algae.utils import raiseif
from ..earthtime import EarthTime
from ..explore.response import Hit, Miss, MissType

DrawnLayer = namedtuple('DrawnLayer', ['name', 'title', 'draw_time', 'draw_calls', 'drawn'])


class Layer(SelectableTool):
    def __init__(self, name: str, category_id: str, earthtime: EarthTime):
        super().__init__(earthtime)
        self.__category_name = ''
        self.__category_id = category_id
        self.__checkbox = None
        self.__description = ''
        self.__name = name
        self.__title = ''

    def __repr__(self):
        return '%s[%s]' % (Layer.__name__, self.__title)

    @classmethod
    def informed(cls, name: str, category_id: str, earthtime: EarthTime):
        layer = cls(name, category_id, earthtime)
        layer.inform()

        return layer

    @staticmethod
    def from_element(layer: Union[Element, Hit], earthtime: EarthTime):
        if isinstance(layer, Element):
            layer = Hit(layer)

        raiseif(
            earthtime is None or bool(earthtime),
            UnearthtimeException('Invalid or inactive EarthTime page.')
        )

        raiseif(
            layer is None or layer.tag_name != 'LABEL',
            UnearthtimeException('Element is not an EarthTime layer.')
        )

        raiseif(
            layer.parent != earthtime.driver,
            UnearthtimeException('Layer is not an element of input EarthTime page.')
        )

        try:
            name = layer.name
            layer = Layer(name, layer.parent_element().parent_element().parent_element()['aria-labelledby'], earthtime)

            if layer.inform():
                return layer
            else:
                raise UnearthtimeException('Element is not an EarthTime layer.')
        except AttributeError:
            raise UnearthtimeException('Element is not an EarthTime layer.')

    @property
    def category_id(self) -> str:
        return self.__category_id

    @property
    def category_name(self) -> str:
        return self.__category_name

    @property
    def checkbox(self) -> Hit:
        return self.__checkbox

    @property
    def description(self) -> str:
        return self.__description

    @property
    def name(self) -> str:
        return self.__name

    @property
    def title(self) -> str:
        return self.__title

    def draw_time(self) -> DrawnLayer:
        if self.inform():
            start = timer()

            self.select()

            drawn = self._earthtime.lastFrameCompletelyDrawn
            draw_calls = 1

            while not drawn:
                sleep(0.5)
                drawn = self._earthtime.lastFrameCompletelyDrawn
                draw_calls += 1

                if not self._earthtime.isSpinnerShowing() and draw_calls >= 60:
                    break

            end = timer()

            self.select()

            total_time = end - start

            return DrawnLayer(self.__name, self.__title, total_time, draw_calls, drawn)

    @returnonexception(False, ElementNotInteractableException)
    def inform(self) -> bool:
        if self._informed:
            return bool(self._earthtime)
        elif self.informable():
            library = self._earthtime.DataLibraryMenu
            header = self._earthtime['CategoryHeader', self.__category_id]
            close_layers = header is Miss
            close_category = False

            if not header:
                library.click()

                if clear := self._earthtime.DataLibrarySearchClearButton:
                    clear.click()

                header = self._earthtime['CategoryHeader', self.__category_id]

                if not header:
                    return False
            elif clear := self._earthtime.DataLibrarySearchClearButton:
                clear.click()

            self.__category_id = header.id_

            if header['aria-selected'] == 'false':
                close_category = True
                header.click()

            label = self._earthtime['LayerLabel', self.__name]
            description = self._earthtime['LayerDescription', self.__name]

            self.__category_name = header.text
            self.__checkbox = self._earthtime['LayerCheckbox', self.__name]
            self.__description = '' if not description else description
            self.__title = label.text.strip()
            self._informed = True

            if close_category:
                header.click()

            if close_layers:
                library.click()

            return True
        else:
            return False

    def is_selected(self) -> bool:
        return bool(self.__checkbox) and self.__checkbox.checked

    @returnonexception(None, StaleElementReferenceException)
    def select(self):
        if self.inform():
            header = self._earthtime['CategoryHeader', self.__category_id]

            if not header:
                self._earthtime.DataLibraryMenu.click()
                header = self._earthtime['CategoryHeader', self.__category_id]

            if header['aria-selected'] == 'false':
                header.click()

            self.__checkbox.click()


class Category(SelectableTool):

    def __init__(self, category_id: str, earthtime: EarthTime):
        super().__init__(earthtime)
        self.__category_id = category_id
        self.__category_name = ''
        self.__layer_names = {}
        self.__layers = []

    def __contains__(self, layer_name: str):
        return layer_name in self.__layer_names

    def __getitem__(self, layer: Union[int, str]) -> Union[Layer, MissType]:
        if isinstance(layer, str) and layer in self.__layer_names:
            return self.__layers[self.__layer_names[layer]]
        elif isinstance(layer, int) and -len(self.__layers) <= layer < len(self.__layers):
            return self.__layers[layer]
        else:
            return Miss

    def __iter__(self):
        for layer in self.__layers:
            yield layer

    def __len__(self):
        return len(self.__layers)

    def __reversed__(self):
        for layer in reversed(self.__layers):
            yield layer

    def __repr__(self):
        if self._informed:
            return '%s [ %s: %s]' % (Category.__name__, self.__category_name, '{\n\t%s\n}' % '\n\t'.join(map(str, self.__layers)))
        else:
            return 'Empty %s' % Category.__name__

    @classmethod
    def informed(cls, category_id: str, earthtime: EarthTime):
        category = cls(category_id, earthtime)
        category.inform()

        return category

    @classmethod
    def from_element(cls, header: Union[Element, Hit], earthtime: EarthTime):
        if isinstance(header, Element):
            header = Hit(header)

        raiseif(
            header is None or header.tag_name != 'H3' or
            not (bool(header['aria-controls']) and header['aria-controls'].startswith('category')),
            UnearthtimeException('Element is not an EarthTime Data Library category.')
        )

        raiseif(
            header.parent != earthtime.driver,
            UnearthtimeException('Category is not an element of input EarthTime page.')
        )

        try:
            category = cls(header.id_, earthtime)

            if category.inform():
                return category
            else:
                raise UnearthtimeException('Element is not an EarthTime Data Library category.')
        except AttributeError:
            raise UnearthtimeException('Element is not an EarthTime Data Library category.')

    @staticmethod
    def layers_by_category(earthtime: EarthTime, inform: bool = False):

        if earthtime is None or not bool(earthtime):
            return {}

        menu = earthtime.DataLibrarySearchInput

        if not menu:
            menu = True
            earthtime.DataLibraryMenu.click()

            if clear := earthtime.DataLibrarySearchClearButton:
                clear.click()
        elif clear := earthtime.DataLibrarySearchClearButton:
            clear.click()

        categories = {category['aria-controls']: Category(category.id_, earthtime) for category in headers} if (headers := earthtime.CategoryHeaders) else {}

        if inform:
            for category in categories.values():
                category.inform()

        if menu:
            earthtime.DataLibraryMenu.click()

        return categories

    @staticmethod
    def layers_by_category_after(category_id: str, earthtime: EarthTime, inform: bool = False):

        if earthtime is None or not bool(earthtime) or noneorempty(category_id):
            return {}

        menu = earthtime.DataLibrarySearchInput

        if not menu:
            menu = True
            earthtime.DataLibraryMenu.click()

            if clear := earthtime.DataLibrarySearchClearButton:
                clear.click()
        elif clear := earthtime.DataLibrarySearchClearButton:
            clear.click()

        categories = {category['aria-controls']: Category(category.id_, earthtime) for category in headers} if (headers := earthtime['CategoryHeadersAfter', category_id]) else {}

        if inform:
            for category in categories.values():
                category.inform()

        if menu:
            earthtime.DataLibraryMenu.click()

        return categories

    @staticmethod
    def layers_by_category_except(category_id: str, earthtime: EarthTime, inform: bool = False):

        if not bool(earthtime) or noneorempty(category_id):
            return {}

        menu = earthtime.DataLibrarySearchInput

        if not menu:
            menu = True
            earthtime.DataLibraryMenu.click()

            if clear := earthtime.DataLibrarySearchClearButton:
                clear.click()
        elif clear := earthtime.DataLibrarySearchClearButton:
            clear.click()

        categories = {category['aria-controls']: Category(category.id_, earthtime) for category in headers} if (headers := earthtime['CategoryHeadersExcept', category_id]) else {}

        if inform:
            for category in categories.values():
                category.inform()

        if menu:
            earthtime.DataLibraryMenu.click()

        return categories

    @property
    def category_id(self) -> str:
        return self.__category_id

    @property
    def category_name(self) -> str:
        return self.__category_name

    @returnonexception(False, ElementNotInteractableException)
    def inform(self) -> bool:
        if self._informed:
            return bool(self._earthtime)
        elif self.informable():
            library = self._earthtime.DataLibraryMenu
            header = self._earthtime['CategoryHeader', self.__category_id]
            close_layers = header is Miss
            close_category = False

            if not header:
                library.click()

                if clear := self._earthtime.DataLibrarySearchClearButton:
                    clear.click()

                header = self._earthtime['CategoryHeader', self.__category_id]

                if not header:
                    return False
            elif clear := self._earthtime.DataLibrarySearchClearButton:
                clear.click()

            self.__category_id = header.id_
            self.__category_name = header.text

            if header['aria-selected'] == 'false':
                close_category = True
                header.click()

            if labels := self._earthtime['CategoryLabels', self.__category_id]:
                layers = [Layer(label.name, self.__category_id, self._earthtime) for label in labels]
                self.__layers = [layer for layer in layers if layer.inform()]
                self.__layer_names = {self.__layers[i].name: i for i in range(len(self.__layers))}
                self._informed = len(layers) == len(self.__layers)

                if close_category:
                    header.click()

                if close_layers:
                    library.click()

            return self._informed
        else:
            return False

    @returnonexception(None, StaleElementReferenceException)
    def select(self):
        if self.inform():
            header = self._earthtime['CategoryHeader', self.__category_id]

            if not header:
                self._earthtime.DataLibraryMenu.click()
                header = self._earthtime['CategoryHeader', self.__category_id]

            if header['aria-selected'] == 'false':
                header.click()

    def time_layers(self) -> list:
        if self._informed and bool(self._earthtime):
            layer_times = []

            library = self._earthtime.DataLibraryMenu
            header = self._earthtime['CategoryHeader', self.__category_id]
            close_layers = header is Miss
            close_category = False

            if not header:
                library.click()

                if clear := self._earthtime.DataLibrarySearchClearButton:
                    clear.click()

                header = self._earthtime['CategoryHeader', self.__category_id]
            elif clear := self._earthtime.DataLibrarySearchClearButton:
                clear.click()

            if header['aria-selected'] == 'false':
                close_category = True
                header.click()

            for layer in self.__layers:
                if time := layer.draw_time():
                    layer_times.append(time)

            if close_category:
                header.click()

            if close_layers:
                library.click()

            return layer_times

        elif self.informable():
            layer_times = []

            library = self._earthtime.DataLibraryMenu
            header = self._earthtime['CategoryHeader', self.__category_id]
            close_layers = header is Miss
            close_category = False

            if not header:
                library.click()

                if clear := self._earthtime.DataLibrarySearchClearButton:
                    clear.click()

                header = self._earthtime['CategoryHeader', self.__category_id]
            elif clear := self._earthtime.DataLibrarySearchClearButton:
                clear.click()

            self.__category_id = header.id_
            self.__category_name = header.text

            if header['aria-selected'] == 'false':
                close_category = True
                header.click()

            if labels := self._earthtime['CategoryLabels', self.__category_id]:
                layers = [Layer(label.name, self.__category_id, self._earthtime) for label in labels]

                for layer in layers:
                    if time := layer.draw_time():
                        self.__layers.append(layer)
                        layer_times.append(time)

                self.__layer_names = {self.__layers[i].name: i for i in range(len(self.__layers))}

                self._informed = len(layers) == len(self.__layers)

                if close_category:
                    header.click()

                if close_layers:
                    library.click()

            return layer_times
        else:
            return []
