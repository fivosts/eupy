#!/usr/bin/env python
import logging
import shell

NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

"""
Wrapper class over logging.Logger to automate formatting and other jobs
"""
class _Logger:

	def __init__(self, name, level, colorize):
		self._colorize = colorize
		self._configLogger(name, level)
		self.debug("Logger initialized")
		return

	def _configLogger(self, name, level):
		# create logger
		logging.root.handlers = []
		self._logger = logging.getLogger(name)
		self._logger.setLevel(level)

		# create console handler and set level to debug
		ch = logging.StreamHandler()
		ch.setLevel(level)

		# create formatter
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

		# add formatter to ch
		ch.setFormatter(formatter)

		# add ch to logger
		if not self._logger.handlers:
			self._logger.addHandler(ch)
			self._logger.propagate = False
			
		self.debug("logger._Logger._configLogger()")
		self.info("Logger has been initialized")
		return

	@property
	def handlers(self):
		return self._logger.handlers

	@property
	def logger(self):
		return self._logger
	
	@property
	def level(self):
		return logging.getLevelName(self._logger.level)
	
	"""
	Main logging functions
	"""
	def debug(self, message):
		if self._colorize:
			message = shell.output(message, shell.bold, shell.green)
		self._logger.debug(message)

	def info(self, message):
		if self._colorize:
			message = shell.output(message, shell.bold, shell.cyan)
		self._logger.info(message)

	def warning(self, message):
		if self._colorize:
			message = shell.output(message, shell.bold, shell.yellow)
		self._logger.warning(message)

	def warn(self, message):
		if self._colorize:
			message = shell.output(message, shell.bold, shell.yellow)
		self._logger.warn(message)

	def error(self, message):
		if self._colorize:
			message = shell.output(message, shell.bold, shell.red)
		self._logger.error(message)
	
	def critical(self, message):
		if self._colorize:
			message = shell.output(message, shell.bold, shell.underline, shell.red)
		self._logger.critical(message)

	def shutdown(self):
		self.debug("eupy.native.logger._Logger.shutdown()")
		logging.shutdown()
		return

_logger = None

def initLogger(name, lvl = INFO, colorize = False):
	global _logger
	_logger = _Logger(name, lvl, colorize)
	_logger.debug("eupy.native.logger.initLogger()")

	return _logger

def getLogger():
	global _logger
	if _logger == None:
		raise NameError("Logger has not been initialized!")
	else:
		_logger.debug("eupy.native.logger.getLogger()")
		return _logger

def initOrGetLogger(name = "", lvl = INFO, colorize = False):
	global _logger
	if _logger == None:
		logging.warning("Logger has not been explicitly initialized")
		_logger = _Logger(name, lvl, colorize)
		_logger.debug("eupy.native.logger.initOrGetLogger()")
		return _logger
	else:
		_logger.debug("eupy.native.logger.initOrGetLogger()")
		return _logger
