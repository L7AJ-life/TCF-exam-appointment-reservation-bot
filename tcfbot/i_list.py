"""
List interface
to be used in future
"""

from typing import (Any, List)


class IList:
    def __init__(self):
        self.__base_list: List[Any] = list()

    def __del__(self):
        self.__base_list.clear()
        del self.__base_list

    def clear(self) -> None:
        """
        clear list
        """
        return self.__base_list.clear()

    def add_item(self, item: Any) -> None:
        """
        Adds item to list
        """
        self.__base_list.append(item)

    def remove_item(self, item: Any) -> None:
        """
        remove item from list
        """

    def count(self) -> int:
        return len(self.__base_list)

    def sort(self) -> None:
        """
        sort base list
        """
        self.__base_list.sort()

    def get_item(self, index: int) -> Any:
        return self.__base_list[index]
    
    def set_item(self, index: int, item: Any) -> None:
        self.__base_list[index] = item

    def __iter__(self):
        return ListIterator(self)


class ListIterator:
    def __init__(self, iter_obj: IList):
        self.iterable_object: IList = iter_obj
        self.index = 0

    def __next__(self):
        if self.index < self.iterable_object.count():
            result = self.iterable_object.get_item(self.index)
            self.index += 1
            return result

        raise StopIteration
