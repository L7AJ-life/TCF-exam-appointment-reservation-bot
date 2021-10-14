import json
import threading

from tcfbot.event import Event, EventList
from tcfbot.payment_day import PaymentDay, PaymentDayList
from tcfbot.account import Account
from tcfbot.reservation import Reservation
from tcfbot.bot import Bot


import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

account = Account(email='lyes.dfgfdgfdg@gmail.com', password='@#gdfgfdgfdg')

event = Event(antenna_name='alger', uid='6130d7adee43a',
              title='TCF SO', antenna_id=1,
              local='alger', price='10000',
              status=1, full=1)

payment_day = PaymentDay(date_to="2021-05-02",
                         event_uid="6130d7adee43a",
                         date_from="2021-05-01",
                         time_shift_uid="6487497497",
                         time_shift_morning=True)

event_list = EventList()
event_list.add_event(event)

payment_day_list = PaymentDayList()
payment_day_list.add_payment_day(payment_day)


def callback(sender, error, data):
    print(sender.session.cookies.items())
    if error:
        print(json.dumps(error))
        return
    print(json.dumps(data))


bot = Bot(account=account,
          events=event_list,
          payment_days=payment_day_list,
          rate_limit=100,
          callback=callback,
          lock=threading.Lock())

bot.run()
