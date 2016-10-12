__author__ = 'Konstantin Glazyrin'

from app.common import logger


class StorageRecaller(logger.LocalLogger):
    """
    Basic general purpose storage
    """
    def __init__(self, parent=None, debug_level=None):
        super(StorageRecaller, self).__init__(name=self.__class__.__name__, parent=parent, debug_level=debug_level)

        # storage for different events
        self.__events = []

    def __len__(self):
        return len(self.__events)

    def __getitem__(self, index):
        res = None
        l = len(self.__events)
        if l > 0 and index < l:
            res = self.__events[index]
        return res

    def __iter__(self):
        return iter(self.__events)

    @property
    def storage(self):
        """
        Returns internal storage
        :return: list()
        """
        return self.__events

    @storage.setter
    def storage(self, value):
        """
        Appends events of any type, but None to the internal storage
        :param value: anything but None
        :return:
        """
        if value is not None:
            self.__events.append(value)

    def length(self):
        """
        Returns length of the internal storage
        :return:
        """
        return len(self)

    def recall_all(self):
        """
        Recalls all methods in __events and clears the __events buffer
        :return:
        """
        for el in self.storage:
            t = str(type(el))
            if 'function' in t or 'instancemethod' in t:
                el()
        # clear information about the events
        self.clear()

    def recall_by_index(self, index):
        """
        Recalls specific event by index
        :param index: int()
        :return: nothing or something, depending on event
        """
        res = None
        el = self[index]
        if el is not None:
            t = str(type(el))
            if 'function' in t or 'instancemethod' in t:
                el()
            else:
                res = el
        return res

    def recall_range(self, start, end):
        """
        Recalls a storage event by range
        :param start: int() - starting index
        :param end: int() - ending index + 1
        :return: list() - results found or None, depending on stored type
        """
        self.info("Restoring range")
        res = None
        for i in range(start, end, 1):
            temp = self.recall_by_index(i)
            if temp is not None:
                if res is None:
                    res = []
                res.append(temp)
        return res

    def recall_type(self, value):
        """
        Retrieves elements of a specific type in the form of a list
        :param value: type(), instance, str() of type
        :return: list()
        """
        res = []
        for el in self.storage:
            t = str(type(value))
            if type(el) == value or isinstance(el, value) or value in t:
                res.append(el)
        return res

    def clear(self):
        """
        Resets internal storage
        :return:
        """
        self.__events = []

    def dummy(self):
        pass