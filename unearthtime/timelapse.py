from _algae.utils import newlambda

from functools import partial

class Timelapse:

	def __init__(self, driver):
		self.__driver = driver

	def __getattr__(self, name):
		res = self.__driver.execute_script('return timelapse.%s' % name)

		if res is None or not (isinstance(res, dict) and len(res) == 0):
			return res
		elif self.__driver.execute_script('return typeof(timelapse.%s)' % name) == 'function':
			length = self.__driver.execute_script('return timelapse.%s.length' % name)
			func = {}
			exec(newlambda(name, length), func)

			return partial(func['f'], self.__driver)