from typing import List, Any


class Member:
    def __init__(self):
        self._base_list: List = list()

    def add_item(self, item: Any) -> None:
        self._base_list.append(item)

    def get_item(self, index: int) -> Any:
        return self._base_list[index]

    def count(self):
        return len(self._base_list)

    def __iter__(self):
        return MemberIterator(self)


class MemberIterator:
    def __init__(self, member: Member):
        self.member: Member = member
        self.__index: int = 0

    def __next__(self):
        if self.__index < member.count():
            item = member.get_item(self.__index)
            self.__index += 1
            return item
        raise StopIteration


member = Member()
member.add_item(1)
member.add_item(2)
member.add_item(3)
member.add_item('4')

for m in member:
    print(m)