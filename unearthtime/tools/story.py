from typing import Union

from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement as Element

from .tool import SelectableTool
from .._algae.deco import returnonexception
from .._algae.exceptions import UnearthtimeException
from .._algae.strings import prefix
from .._algae.utils import raiseif
from ..earthtime import EarthTime
from ..explore.image import Dimension, Thumbnail
from ..explore.response import Hit, Miss, MissType


class Story(SelectableTool):

    def __init__(self, story_id: str, theme_id: str, earthtime: EarthTime):
        super().__init__(earthtime)
        self.__story_id = story_id
        self.__radio = None
        self.__theme = ''
        self.__theme_id = theme_id
        self.__thumbnail = None
        self.__title = ''

    def __repr__(self):
        return f'{Story.__name__}[{self.__title}]'

    @property
    def story_id(self):
        return self.__story_id

    @property
    def theme(self):
        return self.__theme

    @property
    def theme_id(self):
        return self.__theme_id

    @property
    def thumbnail(self) -> Thumbnail:
        return self.__thumbnail

    @property
    def title(self):
        return self.__title

    @returnonexception(False, ElementNotInteractableException)
    def inform(self) -> bool:
        if self._informed:
            return bool(self._earthtime)
        elif self.informable():
            stories = self._earthtime.StoriesMenu
            header = self._earthtime['ThemeHeader', self.__theme_id]
            close_stories = header is Miss
            close_theme = False

            if not header:
                stories.click()
                header = self._earthtime['ThemeHeader', self.__theme_id]

                if not header:
                    return False

            self.__theme_id = header.id_

            if header['aria-selected'] == 'false':
                close_theme = True
                header.click()

            self.__theme = header.text
            self.__radio = self._earthtime['StoryRadioButton', self.__story_id]
            self.__title = self._earthtime['StoryTitle', self.__story_id].text

            src = self._earthtime['StoryThumbnail', self.__story_id].src

            wstart, hstart = src.find('width=') + 6, src.find('height=') + 7
            wstop, hstop = src.find('&', wstart), src.find('&', hstart)

            dim = Dimension(int(src[wstart:wstop]), int(src[hstart:hstop]))

            self.__thumbnail = Thumbnail(src, dim)
            self._informed = True

            if close_theme:
                header.click()

            if close_stories:
                stories.click()

        return self._informed

    @returnonexception(None, StaleElementReferenceException)
    def select(self):
        if self.inform():
            header = self._earthtime['ThemeHeader', self.__theme_id]

            if not header:
                self._earthtime.StoriesMenu.click()
                header = self._earthtime['ThemeHeader', self.__theme_id]

            if header['aria-selected'] == 'false':
                header.click()

            self.__radio.click()


class Theme(SelectableTool):

    def __init__(self, theme_id: str, earthtime: EarthTime):
        super().__init__(earthtime)
        self.__theme_name = ''
        self.__stories = []
        self.__story_ids = {}
        self.__theme_id = theme_id

    def __contains__(self, name: str):
        return prefix(name, 'story_') in self.__story_ids

    def __getitem__(self, key: Union[int, str]) -> Union[Story, MissType]:
        if isinstance(key, int):
            return self.__stories[key] if -len(self.__stories) <= key < len(self.__stories) else Miss
        elif isinstance(key, str) and key in self.__story_ids:
            return self.__stories[self.__story_ids[key]]
        else:
            return Miss

    def __iter__(self):
        for story in self.__stories:
            yield story

    def __len__(self):
        return len(self.__stories)

    def __reversed__(self):
        for story in reversed(self.__stories):
            yield story

    def __repr__(self):
        if self._informed:
            return f'{Theme.__name__} [ {self.__theme_name}: {{\n\t%s\n}}]' % '\n\t'.join(map(str, self.__stories))
        else:
            return f'Empty {Theme.__name__}'

    @classmethod
    def informed(cls, theme_id: str, earthtime: EarthTime):
        theme = cls(theme_id, earthtime)
        theme.inform()

        return theme

    @classmethod
    def from_element(cls, header: Union[Element, Hit], earthtime: EarthTime):
        if isinstance(header, Element):
            header = Hit(header)

            raiseif(
                header is None or header.tag_name != 'H3' or
                not (bool(header['aria-controls']) and header['aria-controls'].startswith('theme')),
                UnearthtimeException('Element is not an EarthTime Stories theme.')
            )

            raiseif(
                header.parent != earthtime.driver,
                UnearthtimeException('Theme is not an element of input EarthTime page.')
            )

            try:
                theme = cls(header.id_, earthtime)

                if theme.inform():
                    return theme
                else:
                    raise UnearthtimeException('Element is not an EarthTime Stories theme.')
            except AttributeError:
                raise UnearthtimeException('Theme is not an element of input EarthTime page.')

    @staticmethod
    def stories_by_theme(earthtime: EarthTime, inform: bool = False):

        if not bool(earthtime):
            return {}

        menu = earthtime.StoriesThemeHeader

        if not menu:
            menu = True
            earthtime.StoriesMenu.click()

        themes = {theme['aria-controls']: Theme(theme.id_, earthtime) for theme in headers} if (headers := earthtime.ThemeHeaders) else {}

        if inform:
            for theme in themes.values():
                theme.inform()

        if menu:
            earthtime.StoriesMenu.click()

        return themes

    @property
    def theme_id(self):
        return self.__theme_id

    @property
    def theme_name(self):
        return self.__theme_name

    @returnonexception(False, ElementNotInteractableException)
    def inform(self) -> bool:
        if self._informed:
            return bool(self._earthtime)
        elif self.informable():
            stories_menu = self._earthtime.StoriesMenu
            header = self._earthtime['ThemeHeader', self.__theme_id]
            close_stories = header is Miss
            close_theme = False

            if not header:
                stories_menu.click()
                header = self._earthtime['ThemeHeader', self.__theme_id]

                if not header:
                    return False

            self.__theme_id = header.id_

            if header['aria-selected'] == 'false':
                close_theme = True
                header.click()

            self.__theme_name = header.text

            if rows := self._earthtime['ThemeStories', self.__theme_id]:
                stories = [Story(story.id_, self.__theme_id, self._earthtime) for story in rows]
                self.__stories = [story for story in stories if story.inform()]
                self.__story_ids = {self.__stories[i].story_id: i for i in range(len(self.__stories))}
                self._informed = len(stories) == len(self.__stories)

                if close_theme:
                    header.click()

                if close_stories:
                    stories_menu.click()

        return self._informed

    @returnonexception(None, StaleElementReferenceException)
    def select(self):
        if self.inform():
            header = self._earthtime['ThemeHeader', self.__theme_id]

            if not header:
                self._earthtime.StoriesMenu.click()
                header = self._earthtime['ThemeHeader', self.__theme_id]

            if header['aria-selected'] == 'false':
                header.click()
