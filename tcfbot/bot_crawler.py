"""
asynchronous bot
fetches reservation events from
if-algerie

login to portal
go to /exams
    fetch events
        crawl events
        event_crawler_callback
        return
    fetch payment days
        crawl payments
        payment_Crawler_callback
        return
    on error
        login and retry
"""

import requests
import ujson as json
import time
import logging
import re
import threading

from typing import Dict, Callable, Any
from urllib3.exceptions import ConnectTimeoutError

from tcfbot.account import Account
from tcfbot.event import EventList
from tcfbot.payment_day import PaymentDay, PaymentDayList

# logger
logger = logging.getLogger(__file__)

# exceptions


class LoginError(Exception):
    pass


class FetchEventError(Exception):
    pass


class NotLoggedInError(Exception):
    pass


class FetchPaymentDayError(Exception):
    pass


class CrawlerBot:
    # init some stuff
    headers = dict()
    headers['Host'] = 'portail.if-algerie.com'
    headers['Accept'] = '*/*'
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                             AppleWebKit/537.36 (KHTML, like Gecko) Chrom\
                             e/91.0.4472.164 Safari/537.36'
    headers['Accept-Language'] = 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
    headers['Connection'] = 'keep-alive'

    session = requests.Session()
    csrf: str = ''
    # constructor

    def __init__(self, **kwargs):
        """
        crawler bot
        @params
            account: Account class object
            callback: Function callback when bot job was done
                @params:
                    sender: self: Bot, error: Dict, data: Dict
            event_list: open event list
            payment_days: PaymentDayList associated to event_list events
            rate_limit: sleep time in (ms) to avoid api bans
        """
        self.account: Account = kwargs.get('account', Account())
        self.event_crawler_callback: Callable = kwargs.get('event_crawler_callback', None)
        self.payment_day_crawler_callback: Callable = kwargs.get('payment_day_crawler_callback', None)
        self.rate_limit = kwargs.get('rate_limit', 200) % 10000

    def call_event_crawler_callback(self, error: Dict[str, Any], data: Dict[str, Any]) -> None:
        if self.event_crawler_callback is not None:
            try:
                self.event_crawler_callback(self, error, data)
            except Exception as e:
                logger.error(f'call_callback error: {e}')

    def call_payment_day_crawler_callback(self, error: Dict[str, Any], data: Dict[str, Any]) -> None:
        if self.payment_day_crawler_callback is not None:
            try:
                self.payment_day_crawler_callback(self, error, data)
            except Exception as e:
                logger.error(f'call_callback error: {e}')

    def login(self) -> None:
        """
        login method: login() -> bool:
        login to account,
        success: fetches,
        else: callback(err, data)
        """
        head = self.headers.copy()
        self.session.cookies.clear()  # clear session cookies
        while True:
            try:
                # get csrf
                req = self.session.get('https://portail.if-algerie.com/login',
                                       headers=head, verify=False, timeout=10)
                csrf_token = re.findall('(?<=<meta name="csrf-token" content=")(.*?)(?=")', req.text)[0]

                # rate limit
                time.sleep(self.rate_limit / 1000)

                # post login
                head['X-CSRF-TOKEN'] = csrf_token
                head['X-Requested-With'] = 'XMLHttpRequest'
                data = {
                        'rt': 'https://portail.if-algerie.com/exams',
                        'email': self.account.email,
                        'password': self.account.password
                        }
                req = self.session.post('https://portail.if-algerie.com/login',
                                        headers=head, data=data, verify=False, timeout=10)


                #check login
                res = req.json()
                if res.get('notification', {}).get('importance', '') != 'success':
                    raise LoginError(f"login failed: f'{json.dumps(res)}")

                # rate limit
                csrf = ''
                while not csrf:
                    logger.warning('fetching csrf token')
                    time.sleep(self.rate_limit / 1000)
                    req = self.session.get('https://portail.if-algerie.com/exams',
                                           headers=head, verify=False, timeout=10)
                    csrf = ''.join(re.findall('(?<=<meta name="csrf-token" content=")(.*?)(?=")', req.text))
                    if csrf:
                        self.csrf = csrf

                #if not self.csrf:
                #    raise LoginError("Couldn't fetch csrf token")
                return
            except ConnectTimeoutError:
                # log exception and increment
                logger.error(f'login error: ConnectTimeoutError')
                logger.warning(f'login Retrying...')
            except Exception as e:
                raise LoginError(json.dumps({
                    'error': 'login error',
                    'message': f'exception occurred: {e}'
                }))

    def is_logged_in(self) -> bool:
        return len(self.session.cookies.get('ifa_session', '')) > 0 and \
               len(self.session.cookies.get('XSRF-TOKEN', '')) > 0

    def crawl_events(self) -> EventList:
        """
        place a reservation
        """
        head = self.headers.copy()
        while True:
            try:
                time.sleep(self.rate_limit / 1000)
                req = self.session.get('https://portail.if-algerie.com/exams',
                                       headers=head, verify=False, timeout=10)
                if req.url.find('/login') >= 0:
                    raise NotLoggedInError('account not logged in')

                csrf = ''.join(re.findall('(?<=<meta name="csrf-token" content=")(.*?)(?=")', req.text))
                if csrf:
                    self.csrf = csrf
                event_list = EventList()
                if not event_list.parse_events(req.text):
                    raise FetchEventError('Could not fetch events data')

                return event_list
            except ConnectTimeoutError:
                logger.error(f'crawl_events error: ConnectTimeoutError')
                logger.warning(f'crawl_events Retrying...')
            except NotLoggedInError as e:
                raise NotLoggedInError(f'{e}')

            except Exception as e:
                raise FetchEventError(json.dumps({
                    'error': 'crawl_events error',
                    'message': f'exception occurred: {e}'
                }))

    def clear_session(self):
        self.session.cookies.clear()

    def crawl_payment_days(self, event_list: EventList) -> PaymentDayList:
        """
        crawl payment days of specified
        event list
        """
        head = self.headers.copy()
        head['X-Requested-With'] = 'XMLHttpRequest'
        head['X-CSRF-TOKEN'] = self.csrf
        head['Referer'] = 'https://portail.if-algerie.com/exams'

        payment_day_list = PaymentDayList()
        for event in event_list:
            logger.warning(f"fetching payment days for event: {event.uid}")
            retires = 0
            while True:
                time.sleep(self.rate_limit / 1000)
                data = {'uid': event.uid, 'service_type': 'EX'}
                try:
                    req = self.session.post('https://portail.if-algerie.com/exams/getdays',
                                            headers=head, data=data, timeout=10)
                    res = req.json()

                    if res.get('success', False):
                        for i in range(len(res.get('dates', []))):
                            payment_day = PaymentDay(event_uid=event.uid,
                                                     date_from=res.get('dates')[i].get('info', {}).get('From', ''),
                                                     date_to=res.get('dates')[i].get('info', {}).get('To', ''),
                                                     time_shift_uid=res.get('dates')[i].get('timeShift', {})
                                                     .get('uid', ''),
                                                     time_shift_morning=res.get('dates')[i].get('timeShift', {})
                                                     .get('is_Morning', False))
                            payment_day_list.add_payment_day(payment_day)
                    else:
                        logger.warning(f'Could not fetch payment days list')
                        logger.warning(f'Response: {json.dumps(res)}')
                    break
                except ConnectTimeoutError:
                    logger.error(f'crawl_payment_days error: ConnectTimeoutError')
                    logger.warning(f'crawl_payment_days Retrying...')

                except Exception as e:
                    logger.error(f"Exception: {e}")
        return payment_day_list

    def bot_worker_event(self) -> None:
        """
        crawl events worker procedure
        """
        try:
            if not self.is_logged_in():
                self.login()

            event_list = self.crawl_events()

            self.call_event_crawler_callback(None, {
                'success': True,
                'event_list': event_list,
                'message': 'successfully crawled events'
            })
            return
        except LoginError as le:
            self.call_event_crawler_callback({
                'error': 'LoginError',
                'message': f'{le}'
            }, None)
        except NotLoggedInError as r_e:
            self.call_event_crawler_callback({
                'error': 'NotLoggedInError',
                'message': f'{r_e}'
            }, None)
        except FetchEventError as fe:
            self.call_event_crawler_callback({
                'error': 'FetchEventError',
                'message': f'{fe}'
            }, None)
        # extra run-time exceptions maybe thrown
        except Exception as e:
            self.call_event_crawler_callback({
                'error': 'Exception',
                'message': f'{e}'
            }, None)

    def bot_worker_payment(self, event_list: EventList) -> None:
        """
        crawl payments procedure
        """
        try:
            payment_day_list = self.crawl_payment_days(event_list=event_list)

            self.call_payment_day_crawler_callback(None, {
                'success': True,
                'payment_day_list': payment_day_list,
                'event_list': event_list,
                'message': 'successfully crawled payment days'
            })
            return
        except FetchPaymentDayError as fe:
            self.call_event_crawler_callback({
                'error': 'FetchPaymentDayError',
                'message': f'{fe}'
            }, None)
        # extra run-time exceptions maybe thrown
        except Exception as e:
            self.call_event_crawler_callback({
                'error': 'Exception',
                'message': f'{e}'
            }, None)

    def run_event_crawler(self):
        """
        asynchronous event crawler
        """
        t = threading.Thread(target=self.bot_worker_event)
        t.start()

    def run_payment_crawler(self, event_list: EventList):
        """
        asynchronous payment days crawler
        """
        t = threading.Thread(target=self.bot_worker_payment, args=(event_list,))
        t.start()
