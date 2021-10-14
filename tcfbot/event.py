"""
Event data class
if-algerie exams
"""
from typing import (Any, Dict, List, Iterable)
import ujson as json
import html
import re
import logging
from tcfbot.account import Account
from tcfbot.enums import exam_data

logger = logging.getLogger(__name__)


class Event:
    def __init__(self, **kwargs):
        """
        Event data
        """
        self.uid: str = kwargs.get('uid', '')
        self.title: str = kwargs.get('title', '')
        self.start_date: str = kwargs.get('start', '')
        self.price: str = kwargs.get('price', '0')
        self.antenna_id: int = kwargs.get('antenna_id', 1)
        self.antenna_name: str = kwargs.get('antenna_name', '')
        self.local: str = kwargs.get('local', '')
        self.status: int = kwargs.get('status', 0)
        self.full: int = kwargs.get('full', 0)

    def __del__(self):
        del(self.uid,
            self.title,
            self.start_date,
            self.price,
            self.antenna_id,
            self.antenna_name,
            self.local,
            self.status,
            self.full)

    def is_full(self) -> bool:
        """
        checks if current event sits are full
        returns True if no sits available
        """
        return self.full == 1

    def is_open(self):
        """
        checks if reservation open for current event
        """
        return self.status == 1

    def can_reserve(self):
        """
        checks if user reservation is possible
        for the current event
        """
        return not self.is_full()

    def json(self) -> Dict[str, Any]:
        """
        returns current events data
        as dictionary object (json like)
        """
        return {
            'uid': self.uid,
            'title': self.title,
            'start_date': self.start_date,
            'price': self.price,
            'antenna_name': self.antenna_name,
            'antenna_id': self.antenna_id,
            'local': self.local,
            'status': self.status,
            'full': self.full
        }

    def text(self) -> str:
        """
        returns simple text representation
        of current event's data
        """
        return f"""uid: {self.uid},
title: {self.title},
start_date: {self.start_date},
price: {self.price},
antenna_name: {self.antenna_name},
antenna_id: {self.antenna_id},
local: {self.local},
status: {self.status},
full: {self.full}"""


class EventList:
    def __init__(self):
        """constructor"""
        self.__events: List[Event] = list()

    def __del__(self):
        """destructor"""
        self.__events.clear()
        del self.__events

    def add_event(self, event: Event) -> bool:
        """returns true on success"""
        if type(event) == Event:
            self.__events.append(event)
            return True
        return False

    def get_item(self, index: int) -> Event:
        """return Event at @index"""
        return self.__events[index]

    def set_item(self, index: int, item: Event) -> None:
        """set event at index"""
        if type(item) != Event:
            raise Exception(f"set_item unsupported type: {type(item)}")
        self.__events[index] = item

    def remove_event(self, event: Event) -> bool:
        """
        remove event from list
        """
        try:
            self.__events.remove(event)
            return True
        except Exception as e:
            logger.error(f'remove_event failed: {e}')
        return False

    def parse_events(self, text: str) -> bool:
        """
        parse events from html page
        """
        try:
            text = html.unescape(text)
            data = re.findall('(?<=defaultEvents\s\W\s)(.*)(?=\]\;)', text,
                              re.DOTALL | re.MULTILINE | re.VERBOSE | re.IGNORECASE)

            data = ''.join(data) + ']'
            for word in ["uid", "title", "start", "duration", "minutes", "className", "level", "price", "antenna_name",
                         "antenna_id", "local", "status", "full"]:
                data = data.replace(word, f'"{word}"')
            data = data.replace('\n', '')
            data = ','.join([d.strip() for d in data.split(',')])
            data = '}'.join([d.strip() for d in data.split('}')])
            data = '{'.join([d.strip() for d in data.split('{')])
            data = data.replace(',]', ']')

            data = json.loads(data)

            for event in data:
                if int(event.get('antenna_id', 1)) == 1:
                    self.add_event(Event(
                        uid=event.get('uid', ''),
                        title=event.get('title', ''),
                        start_date=event.get('start', ''),
                        price=event.get('price', '0'),
                        antenna_id=int(event.get('antenna_id', 1)),
                        antenna_name=event.get('antenna_name', ''),
                        local=event.get('local', ''),
                        status=int(event.get('status', 0)),
                        full=int(event.get('full', 0)),
                    ))
            return True
        except Exception as e:
            logger.error(f'Exception in parse_events: {e}')
        return False

    def clear(self):
        return self.__events.clear()

    def get_account_open_events(self, account: Account) -> Iterable:
        """return open events"""
        event_list = EventList()
        for event in self.__events:
            if event.can_reserve() and \
                event.antenna_id == account.antenna and \
                    event.title == exam_data.get(account.exam, 'TCF SO'):
                event_list.add_event(event)
        return event_list

    def get_open_events(self) -> Iterable[Event]:
        """return open events"""
        event_list = EventList()
        for event in self.__events:
            if event.can_reserve():
                event_list.add_event(event)
        return event_list

    def count(self):
        return len(self.__events)

    def json(self) -> Dict:
        return {
                'events': [event.json() for event in self.__events]
            }

    def __iter__(self):
        return EventListIterator(self)


class EventListIterator:
    def __init__(self, event_list: EventList):
        self._event_list: EventList = event_list
        self._index = 0

    def __next__(self):
        if self._index < self._event_list.count():
            result = self._event_list.get_item(self._index)
            self._index += 1
            return result
        raise StopIteration
