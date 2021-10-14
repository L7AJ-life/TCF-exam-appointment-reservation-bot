from typing import Dict, List, Any
from tcfbot.account import Account
from tcfbot.event import Event
from tcfbot.payment_day import PaymentDay

import logging

logger = logging.getLogger(__name__)


class Reservation:
    def __init__(self, **kwargs):
        self.account: Account = kwargs.get('account', Account())
        self.event: Event = kwargs.get('event', Event())
        self.payment_day: PaymentDay = kwargs.get('payment_day', PaymentDay())

    def text(self) -> str:
        """
        return reservation details
        in raw text
        """
        return  f"""
Account: ######################## 
{self.account.text()}

Event:   ########################
{self.event.text()}

Payment: ########################
{self.payment_day.text()}
"""

    def json(self) -> Dict[str, Any]:
        """
        return Dict of reservation data
        JSON like object
        """
        return {
            'account': self.account.json(),
            'event': self.event.json(),
            'payment_day': self.payment_day.json()
        }


class ReservationList:
    def __init__(self):
        """
        reservations constructor method
        """
        self.__reservations: List[Reservation] = list()

    def __del__(self):
        for reservation in self.__reservations:
            del reservation
        del self.__reservations

    def add_reservation(self, reservation: Reservation) -> bool:
        """
        add reservation item to base list
        """
        if type(reservation) == Reservation:
            self.__reservations.append(reservation)
            return True
        return False

    def remove_reservation(self, reservation: Reservation) -> None:
        """remove reservation from base list"""
        try:
            self.__reservations.remove(reservation)
        except Exception as e:
            logger.error(f"remove_reservation exception: {e}")

    def get_item(self, index: int) -> Reservation:
        return self.__reservations[index]

    def set_item(self, index: int, item: Reservation) -> None:
        if type(item) != Reservation:
            raise Exception(f"set_item unsupported type: {type(item)}")
        self.__reservations[index] = item

    def clear(self):
        return self.__reservations.clear()

    def count(self):
        return len(self.__reservations)

    def json(self) -> Dict:
        return {
            'reservations': [reservation.json() for reservation in self.__reservations]
        }

    def __iter__(self):
        return ReservationListIterator(self)


class ReservationListIterator:
    def __init__(self, reservation_list: ReservationList):
        self._reservation_list: ReservationList = reservation_list
        self._index = 0

    def __next__(self):
        if self._index < self._reservation_list.count():
            result = self._reservation_list.get_item(self._index)
            self._index += 1
            return result
        raise StopIteration
