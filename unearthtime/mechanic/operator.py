from __future__ import annotations
from _algae.exceptions import UnearthtimeException
from _algae.utils import raiseif

from abc import ABC, abstractmethod
from environment import Environment

_Invalid_Attributes = {'explore', 'run', 'quit', 'release_driver', 'driver', 'back', 'close', 'forward', 'goto'}

class Operator(ABC):

	def __init__(self, env: Environment):
		raiseif(
			not isinstance(env, Environment),
			UnearthtimeException(':[%r]: Input is not an UnearthTime env.' % env))

		self._env = env
		self._has_been_informed = False

	def __getattr__(self, key: str):
		if key not in set(filter(lambda x: not x.startswith('_') and x not in _Invalid_Attributes, dir(self._env))):
			raise AttributeError(':[%r]: %s does not contain attribute.' % (key, self.__name__))
		else:
			return self.__env.__getattribute__(key)

	def __call__(self, key: Union[str, tuple]): return self._env(key)
	
	def __getitem__(self, key: Union[str, tuple]): return self._env[key]

	def is_informable(self): return not self._has_been_informed and bool(self._env)

	@abstractmethod
	def inform(self) -> bool: return False

	def reinform(self):
		self._has_been_informed = False
		self.inform()

class SelectableOperator(Operator):

	@abstractmethod
	def select(self):
		pass