from __future__ import annotations

from _algae.exceptions import UnearthtimeException
from _algae.typing import WebObject
from _algae.utils import raiseif
from _algae.warnings import overridinguseof

from .query import By, find, findall, Response, Wait
from .response import Hit, HitList, Miss

from dataclasses import dataclass
from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webelement import WebElement as Element
from typing import Callable, Iterable, Union

__all__ = ['Locator', 'ForcedLocator']

@dataclass
class Locator:
	"""A 'self-aware' element locator

	Attributes:
	- `terms`
		* A string, method that receives strings and returns a string, or list of strings and/or methods

		* The `term` is used to find element in the DOM. It can
		represent an element id, class, name, etc...

	- `by`: optional
		* An optional enum value signaling what the `term` represents. Defaults to
		By.CSS

	- `list_`: optional
		* A optional flag signaling whether or not to search for a single (default) or list of elements

	- `until`: optional
		* An optional permanent wait condition to apply when trying to retrieve this element.

		* It should be either a method or lambda expression accepting a `WebElement`
		and returning `True` or `False`

	Examples:
	
	```py
	>>> from selenium.webdriver import Chrome
	>>> 
	>>> drv = Chrome('drivers/chromedriver.exe')
	>>> drv.get('https://earthtime.org/explore')
	>>> drv.maximize_window()
	>>> 
	>>> logo = Locator('menu-logo', By.ID)
	>>> logo
	Locator[Term: menu-logo, By: ID]::Hit
	>>>
	>>> logo(drv)
	Hit[a1bd9191-86d3-471d-8bb6-a9e4c57b3a80]
	>>>
	>>> cid = 'category-biodiversity'
	>>> cheader = Locator(lambda ac: "h3[aria-controls='%s']" % ac)
	>>> ctable = Locator(lambda alb: 'table#%s')
	>>> 
	>>> cheader(drv, cid)
	Hit[67c23942-f825-42b7-9b40-f4f64d2b1a9e]
	>>> ctable(drv, cid)
	Hit[00dcd198-608f-4f1f-8c14-fb594eeb6eee]
	>>> 
	>>> from selenium.webdriver.support import expected_conditions as EC
	>>> 
	>>> legend_no_ec = Locator('layers-legend', By.ID)
	>>> legend_with_ec = Locator('layers-legend', By.ID, until=EC.visibility_of)
	>>> 
	>>> legend_no_ec(drv)
	Hit[7099af01-2a98-44f9-8a14-c93fcf762111]
	>>>
	>>> legend_with_ec(drv)
	Miss
	>>> 
	```
	"""
	terms: Union[str, Callable, Iterable[Callable]]
	by: Union[By, Iterable[By]] = By.CSS
	list_: bool = False
	until: Wait = None

	def __call__(self, parent: WebObject, *args, until: Wait = None, **kwargs) -> Response:
		raiseif(
			(bool(args) or bool(kwargs)) and not (
				callable(self.terms) or 
				(isinstance(self.terms, Iterable) and any(map(callable, self.terms)))), 
			UnearthtimeException('Term does not take any arguments.'))

		raiseif(
			not (bool(args) or bool(kwargs)) and (
				callable(self.terms)  or 
				(isinstance(self.terms, Iterable) and any(map(callable, self.terms)))), 
			UnearthtimeException('Not enough arguments for term.'))

		raiseif(
			parent is None, 
			UnearthtimeException('No parent to find this element from.'))

		if until and self.until:
			overridinguseof(self.until, until)
		else:
			until = self.until

		if isinstance(self.terms, Iterable) and not isinstance(self.terms, str):
			if isinstance(self.by, Iterable):
				raiseif(
					len(self.terms) != len(self.by),
					UnearthtimeException('Insufficient term-by pairs.')
				)

				for term, by in zip(self.terms, self.by):
					query = term(*args, **kwargs) if callable(term) else term

					if self.list_:
						if (hits := findall(query, by, parent, until)) and hits.where(lambda x: x.is_displayed()):
							return hits
					elif (hit := find(query, by, parent, until)) and hit.is_displayed():
							return hit
				else:
					return Miss
			else:
				for term in self.terms:
					query = term(*args, **kwargs) if callable(term) else term
					
					if self.list_:
						if (hits := findall(query, self.by, parent, until)) and hits.where(lambda x: x.is_displayed()):
							return hits
					elif (hit := find(query, self.by, parent, until)) and hit.if_(lambda x: x.is_displayed()):
							return hit
				else:
					return Miss

		else:
			query = self.terms(*args, **kwargs) if callable(self.terms) else self.terms

			if self.list_:
				if (hits := findall(query, self.by, parent, until)) and hits.where(lambda x: x.is_displayed()):
					return hits
				else:
					return Miss
			elif (hit := find(query, self.by, parent, until)) and hit.if_(lambda x: x.is_displayed()):
					return hit
			else:
				return Miss

	def __repr__(self):
		if isinstance(self.terms, Iterable) and not isinstance(self.terms, str):
			if isinstance(self.by, Iterable):
				raiseif(
					len(self.terms) != len(self.by),
					UnearthtimeException('Insufficient term-by pairs.')
				)

				return "[\n\t%s\n]" % '\n\t'.join(
					["Locator[Term: %s, By: %s] \u2192 %s" % (
						term, 
						by.value.display_name.lstrip('by-').replace('-', ' ').upper(), 
						'HitList' if self.list_ else 'Hit') for term, by in zip(self.terms, self.by)])
			else:
				return "[\n\t%s\n]" % '\n\t'.join(
					["Locator[Term: %s, By: %s] \u2192 %s" % (
						term, 
						self.by.value.display_name.lstrip('by-').replace('-', ' ').upper(), 
						'HitList' if self.list_ else 'Hit') for term in self.terms])
		else:
			return "Locator[Term: %s, By: %s] \u2192 %s" % ( 
			self.terms,
			self.by.value.display_name.lstrip('by-').replace('-', ' ').upper(),
			'HitList' if self.list_ else 'Hit')

class ForcedLocator(Locator):

	@classmethod
	def from_locator(cls, locator: Locator): return cls(locator.terms, locator.by, locator.list_, locator.until)

	def __call__(self, parent: WebObject, *args, until: Wait = None, **kwargs) -> Response:
		raiseif(
			(bool(args) or bool(kwargs)) and not (
				callable(self.terms) or 
				(isinstance(self.terms, Iterable) and any(map(callable, self.terms)))), 
			UnearthtimeException('Term does not take any arguments.'))

		raiseif(
			not (bool(args) or bool(kwargs)) and (
				callable(self.terms)  or 
				(isinstance(self.terms, Iterable) and any(map(callable, self.terms)))), 
			UnearthtimeException('Not enough arguments for term.'))

		raiseif(
			parent is None, 
			UnearthtimeException('No parent to find this element from.'))

		if until and self.until:
			overridinguseof(self.until, until)
		else:
			until = self.until

		if isinstance(self.terms, Iterable) and not isinstance(self.terms, str):
			if isinstance(self.by, Iterable):
				raiseif(
					len(self.terms) != len(self.by),
					UnearthtimeException('Insufficient term-by pairs.')
				)

				for term, by in zip(self.terms, self.by):
					query = term(*args, **kwargs) if callable(term) else term

					if self.list_:
						if (hits := findall(query, by, parent, until)):
							return hits
					elif (hit := find(query, by, parent, until)):
							return hit
				else:
					return Miss
			else:
				for term in self.terms:
					query = term(*args, **kwargs) if callable(term) else term
					
					if self.list_:
						if (hits := findall(query, self.by, parent, until)):
							return hits
					elif (hit := find(query, self.by, parent, until)):
							return hit
				else:
					return Miss

		else:
			query = self.terms(*args, **kwargs) if callable(self.terms) else self.terms

			if self.list_:
				if (hits := findall(query, self.by, parent, until)):
					return hits
				else:
					return Miss
			elif (hit := find(query, self.by, parent, until)):
					return hit
			else:
				return Miss

	def __repr__(self):
		if isinstance(self.terms, Iterable) and not isinstance(self.terms, str):
			if isinstance(self.by, Iterable):
				raiseif(
					len(self.terms) != len(self.by),
					UnearthtimeException('Insufficient term-by pairs.')
				)

				return "[\n\t%s\n]" % '\n\t'.join(
					["ForcedLocator[Term: %s, By: %s] \u2192 %s" % (
						term, 
						by.value.display_name.lstrip('by-').replace('-', ' ').upper(), 
						'HitList' if self.list_ else 'Hit') for term, by in zip(self.terms, self.by)])
			else:
				return "[\n\t%s\n]" % '\n\t'.join(
					["ForcedLocator[Term: %s, By: %s] \u2192 %s" % (
						term, 
						self.by.value.display_name.lstrip('by-').replace('-', ' ').upper(), 
						'HitList' if self.list_ else 'Hit') for term in self.terms])
		else:
			return "Locator[Term: %s, By: %s] \u2192 %s" % ( 
			self.terms,
			self.by.value.display_name.lstrip('by-').replace('-', ' ').upper(),
			'HitList' if self.list_ else 'Hit')