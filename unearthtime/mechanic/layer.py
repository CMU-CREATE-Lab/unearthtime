from __future__ import annotations
from _algae.deco import returnonexception
from _algae.exceptions import UnearthtimeException
from _algae.typing import ElementPredicate
from _algae.utils import raiseif
from .operator import SelectableOperator

from collections import namedtuple
from environment import Environment
from explore.query import Miss
from explore.response import Hit
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webelement import WebElement as Element
from time import sleep
from timeit import default_timer as timer
from typing import Callable, Iterable, Union

DrawnLayer = namedtuple('DrawnLayer', ['title', 'draw_time', 'draw_calls', 'was_drawn'])

class Layer(SelectableOperator):

	def __init__(self, name: str, category_id: str, env: Environment):
		super().__init__(env)
		self.__category = ''
		self.__category_id = category_id
		self.__checkbox = None
		self.__description = ''
		self.__name = name
		self.__title = ''

	def __repr__(self): return '%s[%s]' % (Layer.__name__, self.__title)

	@staticmethod
	def from_element(layer: Union[Hit, Element], env):
		raiseif(
			layer is None or layer.tagName != 'LABEL', 
			UnearthtimeException('Element is not a layer.'))

		raiseif(
			layer._element._parent != env.driver, 
			UnearthtimeException('Layer not found using environment driver.'))

		try:
			name = layer.name
			layer = Layer(name, layer.parent().parent().parent()['aria-labelledby'], env)
			
			if layer.inform():
				return layer
			else:
				raise UnearthtimeException('Element is not a layer.')
		except AttributeError:
			raise UnearthtimeException('Element is not a layer.')

	@property
	def category(self) -> str: return self.__category

	@property
	def category_id(self) -> str: return self.__category_id

	@property
	def checkbox(self) -> Hit: return self.__checkbox
	
	@property
	def description(self) -> str: return self.__description

	@property
	def name(self) -> str: return self.__name

	@property
	def title(self) -> str: return self.__title

	@returnonexception(False, ElementNotInteractableException)
	def inform(self) -> bool:
		if self._has_been_informed:
			return bool(self._env)
		elif self.is_informable():
			library = self._env['DataLibraryMenu']
			header = self._env['CategoryHeader', self.__category_id]
			close_layers = header is Miss
			close_cat = False

			if not header:
				library.click()

				if (clear := self._env['DataLibrarySearchClearButton']):
					clear.click()

				header = self._env['CategoryHeader', self.__category_id]
			elif (clear := self._env['DataLibrarySearchClearButton']):
				clear.click()

			self.__category_id = header['id']
	
			if header['aria-selected'] == 'false':
				close_cat = True
				header.click()

			table = self._env['CategoryTable', self.__category_id]
			label = self._env['LayerLabel', self.__name]
			description = self._env['LayerDescription', self.__name]

			self.__category = header.text
			self.__checkbox = self._env['LayerCheckbox', self.__name]
			self.__description = '' if not description else description
			self.__title = label.text.strip()
			self._has_been_informed = True

			if close_cat:
				header.click()

			if close_layers:
				library.click()

			return True
		else:
			return False

	def is_displayed(self): return self._env['LayerLabel', self.__name].is_displayed()

	@returnonexception(False, StaleElementReferenceException)
	def select(self):
		if self.inform():
			header = self._env['CategoryHeader', self.__category_id]

			if not header:
				self._env['DataLibraryMenu'].click()
				header = self._env['CategoryHeader', self.__category_id]

			if header['aria-selected'] == 'false':
				header.click()

			self.__checkbox.click()

	def draw_time(self):
		if self.inform():
			if self.title:
				start = timer()
				self.select()

				drawn = self._env.lastFrameCompletelyDrawn
				draw_calls = 1

				while not drawn:
					sleep(0.25)
					drawn = self._env.lastFrameCompletelyDrawn
					draw_calls += 1

					if not self._env.isSpinnerShowing() and draw_calls >= 100:
						break
																				
				end = timer()

				self.select()

				ttime = end - start

				return DrawnLayer(self.__title, ttime, draw_calls, drawn)
			else:
				return DrawnLayer('', -1, 0, False)

class Category(SelectableOperator):
	
	def __init__(self, category_id: str, env: Environment):
		super().__init__(env)
		self.__category_id = category_id
		self.__name = ''
		self.__layer_ids = {}
		self.__layers = []

	def __contains__(self, key: str) -> bool: return key in self.__layer_ids

	def __getitem__(self, key: Union[int, str]) -> Union[Layer, Miss]:
		if isinstance(key, int):
			return self.__layers[key] if key >= -len(self.__layers) and key < len(self.__layers) else Miss
		elif isinstance(key, str) and key in self.__layer_ids:
			return self.__layers[self.__layer_ids[key]]
		else:
			return Miss

	def __iter__(self):
		for layer in self.__layers:
			yield layer
			
	def __len__(self) -> int: return len(self.__layers)

	def __reversed__(self):
		for layer in reversed(self.__layers):
			yield layer

	def __repr__(self): return '%s  [ %s: {\n\t%s\n}]' % (Category.__name__, self.__name, '\n\t'.join(map(str, self.__layers)))

	@staticmethod
	def layers_by_category_of(env: Environment, inform: bool =False):
		menu = False

		if not env['DataLibrarySearchInput']:
			menu = True
			env['DataLibraryMenu'].click()
			
		layers = {category['aria-controls'] : Category(category['id'], env) for category in headers } if bool(env) and (headers := env['CategoryHeaders']) else {}

		if inform:
			for category in layers.values():
				category.inform()

		if menu:
			env['DataLibraryMenu'].click()

		return layers

	@staticmethod
	def layers_by_category_after(category_id: str, env: Environment, inform: bool = False):
		menu = False

		if not env['DataLibrarySearchInput']:
			menu = True
			env['DataLibraryMenu'].click()

		layers = {category['aria-controls'] : Category(category['id'], env) for category in headers } if bool(env) and (headers := env['CategoryHeadersAfter', category_id]) else {}

		if inform:
			for category in layers.values():
				category.inform()

		if menu:
			env['DataLibraryMenu'].click()

		return layers

	@staticmethod
	def layers_by_category_except(category_id: str, env: Environment, inform: bool = False):
		menu = False

		if not env['DataLibrarySearchInput']:
			menu = True
			env['DataLibraryMenu'].click()

		layers = {category['aria-controls'] : Category(category['id'], env) for category in headers } if bool(env) and (headers := env['CategoryHeadersExcept', category_id]) else {}

		if inform:
			for category in layers.values():
				category.inform()

		if menu:
			env['DataLibraryMenu'].click()

		return layers
	
	@property
	def category_id(self): return self.__category_id

	@property
	def name(self): return self.__name

	@returnonexception(False, ElementNotInteractableException)
	def inform(self) -> bool:
		if self._has_been_informed:
			return bool(self._env)
		elif self.is_informable():

			library = self._env['DataLibraryMenu']
			header = self._env['CategoryHeader', self.__category_id]
			close_layers = header is Miss
			close_cat = False

			if not header:
				library.click()

				if (clear := self._env['DataLibrarySearchClearButton']):
					clear.click()

				header = self._env['CategoryHeader', self.__category_id]
			elif (clear := self._env['DataLibrarySearchClearButton']):
				clear.click()

			self.__category_id = header.id_
			self.__name = header.text

			if header['aria-selected'] == 'false':
				close_cat = True
				header.click()

			if (labels := self._env['CategoryLabels', self.__category_id]):
				layers = [ Layer(label['name'], self.__category_id, self._env) for label in labels]
				# print('\n'.join(map(str, layers)))

				self.__layers = [ layer for layer in layers if layer.inform() ]
				
				self.__layer_ids = { self.__layers[i].name : i for i in range(len(self.__layers)) }

				self._has_been_informed = len(layers) == len(self.__layers)

				if close_cat:
					header.click()
				
				if close_layers:
					library.click()

			return self._has_been_informed
		else:
			return False

	@returnonexception(False, StaleElementReferenceException)
	def select(self):
		if self.inform():
			header = self._env['CategoryHeader', self.__category_id]

			if not header:
				self._env['DataLibraryMenu'].click()
				header = self._env['CategoryHeader', self.__category_id]
			
			if header['aria-selected'] == 'false':
				header.click()

	def time_layers(self):
		if bool(self._env):
			layer_times = []

			library = self._env['DataLibraryMenu']
			header = self._env['CategoryHeader', self.__category_id]
			close_layers = header is Miss
			close_cat = False

			if not header:
				library.click()

				if (clear := self._env['DataLibrarySearchClearButton']):
					clear.click()

				header = self._env['CategoryHeader', self.__category_id]

			elif (clear := self._env['DataLibrarySearchClearButton']):
				clear.click()

			self.__category_id = header.id_
			self.__name = header.text

			if header['aria-selected'] == 'false':
				close_cat = True
				header.click()

			if (labels := self._env['CategoryLabels', self.__category_id]):
				layers = [ Layer(label['name'], self.__category_id, self._env) for label in labels]
				# print('\n'.join(map(str, layers)))

				for layer in layers:
					if (dlayer := layer.draw_time()):
						self.__layers.append(layer)
						layer_times.append(dlayer)
				
				self.__layer_ids = { self.__layers[i].name : i for i in range(len(self.__layers)) }

				self._has_been_informed = len(layers) == len(self.__layers)

				if close_cat:
					header.click()
				
				if close_layers:
					library.click()

			return layer_times
		else:
			return []
		
class DLSearchResult:

	def __init__(self, label: Element, category: str, env: Environment):
		self.__category = category
		self.__checkbox = label.find_element_by_tag_name('input')
		self._env = env
		self.__label = label
		self.__title = label.text.strip()

	def __repr__(self): return '%s[%s: %s]' % (DLSearchResult.__name__, self.__category, self.__title)

	@property
	def category(self) -> str: return self.__category

	@property
	def label(self) -> Element: return self.__label

	@property
	def title(self) -> str: return self.__title

	def select(self):
		if bool(self._env) and self.__checkbox.is_displayed():
			self.__checkbox.click()

class DLSearchResultList(tuple):
	
	def __new__(cls, query: str='', results: Iterable[DLSearchResult] = None):
		return tuple.__new__(cls, results) if results else tuple.__new__(cls)

	def __init__(self, query: str='', results: Iterable[DLSearchResult] = None):
		self.__query = query

	def __getitem__(self, key: Union[Callable[[Element], bool], int]): return DLSearchResultList(result for result in self if key(result) == True) if callable(key) else super().__getitem__(key)

	def __repr__(self): 
		if len(self) > 0:
			return '%s [ Query: "%s"\n\n\t%s\n]' % (DLSearchResultList.__name__, self.__query, '\n\t'.join(map(str, self)))  
		else: 
			return '%s [ Query: "%s" ]' % (DLSearchResultList.__name__, self.__query)

	@property
	def query(self) -> str: return self.__query

	def selectall(self):
		for result in self:
			result.select()

	def where(self, condition: Callable[[Element], bool]): return DLSearchResultList(result for result in self if condition(result)) if callable(condition) else DLSearchResultList()

class DLSearchEngine:

	def __init__(self, env: Environment):
		self.__clear = None
		self.__empty_results_msg = None
		self._env = env
		self._has_been_informed = False
		self.__input = None
		self.__query = ''
		self.__results = None

	def clear(self):
		if self.inform() and self.__clear.is_displayed():
			self.__clear.click()

	@returnonexception(False, ElementNotInteractableException)
	def inform(self):
		if self._has_been_informed:
			return bool(self._env)
		elif self.is_informable():
			input = self._env['DataLibrarySearchInput']

			if not input:
				self['DataLibraryMenu'].click()
				self.__input = self._env['DataLibrarySearchInput']

			self.__input.send_keys('***')

			self.__clear = self._env['DataLibrarySearchClearButton']
			self.__empty_results_msg = self._env['DataLibraryEmptySearchResultsMessage']

			self.__clear.click()

			self._has_been_informed = True

			return True
		else:
			return False

	@returnonexception(DLSearchResultList(), StaleElementReferenceException)
	def search(self, query: str, clear: bool = True) -> DLSearchResultList:
		if self.inform():
			library = self._env['DataLibraryMenu']

			if not self.__input.is_displayed():
				library.click()

			if clear and self.__clear.is_displayed():
				self.__clear.click()

			self.__input.send_keys(query)

			sleep(0.5)

			if self.__empty_results_msg.is_displayed():
				return DLSearchResultList()

			categories = self._env.pull('DataLibrarySearchFoundCategories')

			results = {}

			for i in range(len(categories) - 1):
				results[categories[i].text] = self._env.pull(('DataLibrarySearchFoundLabelsBetween', categories[i].text, categories[i+1].text))

			results[categories[-1].text] = self._env.pull(('DataLibrarySearchFoundLabelsFollowing', categories[-1].text))

			search_results = []
			search_results.extend([ DLSearchResult(label, category, self._env) 
				for category, labels in results.items()
					for label in labels ])

			return DLSearchResultList(search_results)
		else:
			DLSearchResultList()