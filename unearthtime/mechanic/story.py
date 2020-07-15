from __future__ import annotations
from _algae.deco import returnonexception
from _algae.strings import prefix
from .operator import SelectableOperator

from environment import Environment
from explore.image import Thumbnail
from explore.response import Miss
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webelement import WebElement as Element
from typing import Callable, Iterable, Union

from time import sleep

class Story(SelectableOperator):

	def __init__(self, id: str, theme_id: str, env: Environment):
		super().__init__(env)
		self.__id = id
		self.__radio = None
		self.__theme = ''
		self.__theme_id = theme_id
		self.__thumbnail = None
		self.__title = ''

	def __repr__(self): return '%s[%s]' % (Story.__name__, self.__title)

	@property
	def id(self) -> str: return self.__id

	@property
	def theme(self) -> str: return self.__theme

	@property
	def theme_id(self) -> str: return self.__theme_id

	@property
	def thumbnail(self) -> Thumbnail: return self.__thumbnail

	@property
	def title(self) -> str: return self.__title

	@returnonexception(False, ElementNotInteractableException)
	def inform(self):
		if self._has_been_informed:
			return bool(self._env)
		elif self.is_informable():
			stories = self._env['StoriesMenu']
			header = self._env['ThemeHeader', self.__theme_id]
			close_stories = header is Miss
			close_theme = False

			if not header:
				stories.click()
				header = self._env['ThemeHeader', self.__theme_id]

			self.__theme_id = header.id_

			if header['aria-selected'] == 'false':
				close_theme = True
				header.click()

			table = self._env['ThemeTable', self.__theme_id]

			self.__theme = header.text
			self.__radio = self._env['StoryRadioButton', self.__id]
			self.__title = self._env['StoryTitle', self.__id].text

			src = self._env['StoryThumbnail', self.__id].src

			wstart, hstart = src.find('width=') + 6, src.find('height=') + 7
			wstop, hstop = src.find('&', wstart), src.find('&', hstart)

			w, h = int(src[wstart:wstop]), int(src[hstart:hstop])

			self.__thumbnail = Thumbnail(src, w, h)

			self._has_been_informed = True

			if close_theme:
				header.click()

			if close_stories:
				stories.click()

			return True
		else:
			return False

	@returnonexception(False, StaleElementReferenceException)
	def select(self) -> bool:
		if self.inform():
			header = self._env['ThemeHeader', self.__theme_id]

			if not header:
				self._env['StoriesMenu'].click()
				header = self._env['ThemeHeader', self.__theme_id]

			if header['aria-selected'] == 'false':
				header.click()

			self.__radio.click()

class Theme(SelectableOperator):

	def __init__(self, theme_id: str, env: Environment):
		super().__init__(env)
		self.__name = ''
		self.__stories = []
		self.__story_ids = {}
		self.__theme_id = theme_id

	def __contains__(self, key: str) -> bool: return prefix(key, 'story_') in self.__story_ids

	def __getitem__(self, key: Union[int, str]) -> Union[Story, Miss]:
		if isinstance(key, int):
			return self.__stories[key] if key >= -len(self.__stories) and key < len(self.__stories) else Miss
		elif isinstance(key, str) and (key := prefix(key, 'story_')) in self.__story_ids:
			return self.__stories[self.__story_ids[key]]
		else:
			return Miss
	
	def __iter__(self):
		for story in self.__stories:
			yield story

	def __len__(self): return len(self.__stories)

	def __reversed__(self):
		for story in reversed(self.__stories):
			yield story

	def __repr__(self): return '%s [ %s: {\n\t%s\n}]' % (Theme.__name__, self.__name, '\n\t'.join(map(str, self.__stories)))

	@staticmethod
	def stories_by_theme_of(env: Environment, inform: bool = True): 
		menu = False
		
		if not env['StoriesThemeHeader']:
			menu = True
			env['StoriesMenu'].click()

		themes = {theme['aria-controls'] : Theme(theme.id_, env) for theme in env['ThemeHeaders'] } if bool(env) else {}

		if inform:
			for theme in theme.values():
				theme.inform()

		if menu:
			env['StoriesMenu'].click()

		return themes

	@property
	def name(self): return self.__name

	@property
	def theme_id(self) : return self.__theme_id

	@returnonexception(False, ElementNotInteractableException)
	def inform(self) -> bool:
		if self._has_been_informed:
			return bool(self._env)
		elif self.is_informable():
			stories_menu = self._env['StoriesMenu']
			header = self._env['ThemeHeader', self.__theme_id]
			close_stories = header is Miss
			close_theme = False

			if not header:
				stories_menu.click()
				header = self._env['ThemeHeader', self.__theme_id]

			self.__theme_id = header.id_

			if header['aria-selected'] == 'false':
				close_theme = True
				header.click()

			self.__name = header.text

			if (stories := self._env['ThemeStories', self.__theme_id]):
				stories = [ Story(story.id_, self.__theme_id, self._env) for story in stories]
				self.__stories = [ story for story in stories if story.inform() ]
				self.__story_ids = { self.__stories[i].id : i for i in range(len(self.__stories))}

				self._has_been_informed = len(stories) == len(self.__stories)

				if close_theme:
					header.click()

				if close_stories:
					stories_menu.click()

				sleep(0.5)

			return self._has_been_informed
		else:
			False

	@returnonexception(None, StaleElementReferenceException)
	def select(self):
		if self.inform():
			header = self._env['ThemeHeader', self.__theme_id]

			if not header:
				self._env['StoriesMenu'].click()
				header = self._env['ThemeHeader', self.__theme_id]

			if header['aria-selected'] == 'false':
				header.click()

			

