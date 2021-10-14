from typing import (Any, Dict, List, Iterable)
from tcfbot.event import Event
import logging

logger = logging.getLogger(__name__)


class PaymentDay:
    def __init__(self, **kwargs):
        """PaymentDay object constructor method"""
        self.date_from: str = kwargs.get('date_from', '')
        self.date_to: str = kwargs.get('date_to', '')
        self.time_shift_uid: str = kwargs.get('time_shift_uid', '')
        self.time_shift_morning: str = str(kwargs.get('time_shift_morning', ''))
        self.event_uid: str = kwargs.get('event_uid', '')

    def __del__(self):
        del(
            self.date_from,
            self.date_to,
            self.time_shift_uid,
            self.time_shift_morning,
            self.event_uid
        )

    def text(self):
        """
        returns payment day data in raw format
        """
        return f"""from: {self.date_from}
to: {self.date_to}
time shift uid: {self.time_shift_uid}
time shift morning: {self.time_shift_morning}
event uid: {self.event_uid}"""

    def json(self):
        """
        returns Dict payment day data (JSON like)
        """
        return {
            'from': self.date_from,
            'to': self.date_to,
            'time_shift_uid': self.time_shift_uid,
            'time_shift_morning': self.time_shift_morning,
            'event_uid': self.event_uid
        }


class PaymentDayList:
    def __init__(self):
        """PaymentDayList constructor method"""
        self.__payment_days: List[PaymentDay] = list()

    def __del__(self):
        """PaymentDayList destructor method"""
        for payment_day in self.__payment_days:
            del payment_day
        del self.__payment_days

    def get_item(self, index: int) -> PaymentDay:
        """
        return payment day
        """
        return self.__payment_days[index]

    def set_item(self, index: int, item: PaymentDay):
        if type(item) != PaymentDay:
            raise Exception(f"set_item unsupported type: {type(item)}")
        self.__payment_days[index] = item

    def add_payment_day(self, payment_day: PaymentDay) -> bool:
        """
            Adds paymentDay object to list
            returns True on success
            False on failure
        """
        if type(payment_day) == PaymentDay:
            self.__payment_days.append(payment_day)
            return True
        return False

    def delete_payment_day(self, payment_day) -> bool:
        """
            Deletes the payment day for list
        """
        try:
            self.__payment_days.remove(payment_day)
            return True
        except Exception as e:
            logger.error(f'delete_payment_day failed: {e}')
        return False

    def clear(self):
        """
        Clear base list
        """
        self.__payment_days.clear()

    def count(self):
        """
        return length of base list
        """
        return len(self.__payment_days)

    def json(self) -> Dict[str, Any]:
        return {
            'payment_days': [payment_day.json() for payment_day in self.__payment_days]
        }

    def get_payment_days(self, event: Event) -> Iterable:
        """
        return payment day objects for target event
        """
        payment_day_list = PaymentDayList()
        for payment_day in self.__payment_days:
            if payment_day.event_uid == event.uid:
                payment_day_list.add_payment_day(payment_day)

        return payment_day_list

    def __iter__(self):
        return PaymentDayListIterator(self)


class PaymentDayListIterator:
    def __init__(self, payment_day_list: PaymentDayList):
        self._payment_day_list: PaymentDayList = payment_day_list
        self._index = 0

    def __next__(self):
        if self._index < self._payment_day_list.count():
            result = self._payment_day_list.get_item(self._index)
            self._index += 1
            return result
        raise StopIteration
