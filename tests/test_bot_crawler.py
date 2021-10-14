import json

from tcfbot.event import Event, EventList
from tcfbot.payment_day import PaymentDay, PaymentDayList
from tcfbot.account import Account
from tcfbot.bot_crawler import CrawlerBot
import logging
logging.basicConfig(level=logging.INFO)
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

account = Account(email='lyes.fdfdgfdg@gmail.com', password='@#dfgfdgfdg')

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
    if error:
        print(json.dumps(error))
        return
    event_list = data.get('event_list', EventList())
    print(json.dumps(event_list.json()))
    bot.run_payment_crawler(event_list)

def callback1(sender, error, data):
    if error:
        print(json.dumps(error))
        return
    print(json.dumps(data.get('payment_day_list', PaymentDayList()).json()))


bot = CrawlerBot(account=account,
                 rate_limit=999,
                 event_crawler_callback=callback,
                 payment_day_crawler_callback=callback1)

bot.run_event_crawler()