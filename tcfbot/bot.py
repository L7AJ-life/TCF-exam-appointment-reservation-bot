"""
reservation bot
"""
import requests
import ujson as json
import time
import logging
import re
import threading

from typing import Dict, Callable, Any, Tuple
from urllib3.exceptions import ConnectTimeoutError

from tcfbot.account import Account
from tcfbot.event import Event, EventList
from tcfbot.payment_day import PaymentDay, PaymentDayList
from tcfbot.reservation import Reservation

# logger
logger = logging.getLogger(__file__)

# exceptions


class LoginError(Exception):
    pass


class ReservationError(Exception):
    pass


# reserver
class Bot:
    # init some stuff
    headers = dict()
    headers['Host'] = 'portail.if-algerie.com'
    headers['Accept'] = '*/*'
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                             AppleWebKit/537.36 (KHTML, like Gecko) Chrom\
                             e/91.0.4472.164 Safari/537.36'
    headers['Accept-Language'] = 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
    headers['Connection'] = 'keep-alive'

    csrf: str = ''
    session = requests.Session()

    # constructor
    def __init__(self, **kwargs):
        """
        reserver bot
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
        self.callback: Callable = kwargs.get('callback', None)
        self.event_list: EventList = kwargs.get('events', EventList())
        self.payment_days: PaymentDayList = kwargs.get('payment_days', PaymentDayList())
        self.rate_limit = kwargs.get('rate_limit', 200) % 10000
        self.lock = kwargs.get('lock', None)

    def lock_acquire(self):
        if self.lock:
            self.lock.acquire()

    def lock_release(self):
        if self.lock:
            self.lock.release()

    def call_callback(self, error: Dict[str, Any], data: Dict[str, Any]) -> None:
        if self.callback is not None:
            self.lock_acquire()
            try:
                self.callback(self, error, data)
            except Exception as e:
                logger.error(f'call_callback error: {e}')
            self.lock_release()

    def login(self) -> None:
        """
        login method: login() -> bool:
        login to account,
        success reserves,
        else callback(err, data)
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

                # check login
                res = req.json()
                if res.get('notification', {}).get('importance', '') != 'success':
                    raise LoginError(f"login failed: f'{json.dumps(res)}")

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

    def reserve(self) -> Tuple[Event, PaymentDay]:
        """
        place a reservation
        """

        head = self.headers.copy()
        head['X-Requested-With'] = 'XMLHttpRequest'
        head['X-CSRF-TOKEN'] = self.csrf
        head['Referer'] = 'https://portail.if-algerie.com/exams'

        for event in self.event_list.get_account_open_events(self.account):
            logger.warning(f'Trying event: {event.uid}')
            for payment_day in self.payment_days.get_payment_days(event):
                logger.warning(f'Trying payment day: {payment_day.time_shift_uid}')
                data = {
                        'uid': event.uid,
                        'motivation': self.account.motivation,
                        'timeshift': f'{payment_day.date_from}-{payment_day.date_to}',
                        'info': payment_day.time_shift_uid
                        }

                while True:
                    try:
                        # rate limit
                        time.sleep(self.rate_limit / 1000)

                        req = self.session.post('https://portail.if-algerie.com/exams/reserve',
                                                headers=head, data=data, verify=False, timeout=10)
                        res = req.json()
                        if res.get('success', False):
                            return event, payment_day
                        else:
                            logger.warning(f'Reservation failed:\
                                    \nEvent uid: {json.dumps(data)} \
                                    \nResponse source: {json.dumps(res)}')

                        break
                    except ConnectTimeoutError:
                        logger.error(f'reserve error: ConnectTimeoutError')
                        logger.warning(f'reserve Retrying...')
                    except Exception as e:
                        raise ReservationError(json.dumps({
                            'error': 'login error',
                            'message': f'exception occurred: {e}'
                        }))

        raise ReservationError(json.dumps({
                'error': 'reserve failed',
                'message': 'Could not place reservation'
            }))

    def bot_worker(self):
        """
            reservation procedure
        """
        try:
            self.login()
            event, payment_day = self.reserve()
            self.account.reserved = 1
            reservation = Reservation(account=self.account,
                                      payment_day=payment_day,
                                      event=event)
            self.call_callback(None, {
                'success': True,
                'reservation': reservation,
                'message': f'user {self.account.email} reserved'
            })
            return
        except LoginError as le:
            self.call_callback({
                'error': 'login',
                'message': f'{le}'
            }, None)
        except ReservationError as r_e:
            self.call_callback({
                'error': 'reserve',
                'message': f'{r_e}'
            }, None)
        except Exception as e:
            self.call_callback({
                'error': 'exception',
                'message': f'{e}'
            }, None)

    def run(self):
        """
        asynchronous reservation
        """
        t = threading.Thread(target=self.bot_worker)
        t.start()
