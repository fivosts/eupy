#!/usr/bin/env python
import logging

"""
Wrapper class over logging.Logger to automate formatting and other jobs
"""
class Logger:

	def __init__(self, name):
		self.configLogger(name)
		return

	def _configLogger(self, name):
		
		# create logger
		self._logger = logging.getLogger(name)
		self._logger.setLevel(logging.INFO)

		# create console handler and set level to debug
		ch = logging.StreamHandler()
		ch.setLevel(logging.INFO)

		# create formatter
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

		# add formatter to ch
		ch.setFormatter(formatter)

		# add ch to logger
		self._logger.addHandler(ch)
		return

	"""
	Main logging functions
	"""
	def debug(self, message):
		self._logger.debug(message)

	def info(self, message):
		self._logger.info(message)

	def warning(self, message):
		self._logger.warning(message)

	def warn(self, message):
		self._logger.warn(message)

	def error(self, mesaage):
		self._logger.error(message)
	
	def critical(self, message):
		self._logger.critical(message)

	def shutdown(self):
		logging.shutdown()
		return

	def getLogger(self, name):
		return self._logger
