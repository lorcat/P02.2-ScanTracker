__author__ = 'Konstantin Glazyrin'

import logging

from PyQt4.Qwt5 import  Qwt

class LocalLogger(object):
    """
    Wrapper for logging object
    """
    FORMAT = '%(asctime)-15s %(message)s'
    def __init__(self, name=None, parent=None, debug_level=None):

        if name is None:
            name = self.__class__.__name__

        logging.basicConfig(format=self.FORMAT)
        self._logger = logging.getLogger(name)

        # set debug level same to the parent
        if parent is not None:
            try:
                debug_level = parent.debug_level
            except AttributeError:
                pass

        if debug_level is None:
            debug_level = logging.DEBUG

        self._debug_level = debug_level

        self._logger.setLevel(debug_level)

    @property
    def debug_level(self):
        return self._debug_level

    def log(self, *args):
        return self._logger.log(*args)

    def info(self, *args):
        return self._logger.info(*args)

    def debug(self, *args):
        return self._logger.debug(*args)

    def warning(self, *args):
        return self._logger.warning(*args)

    def error(self, *args):
        return self._logger.error(*args)

    def info_object(self, *args):
        for el in args:
            self.info("Object: (%s) (%s)" % (type(el), repr(el)))

    def classname(self):
        return self.__class__.__name__
