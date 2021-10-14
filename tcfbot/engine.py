"""
Crawls events data and
schedule reservations
"""
import time

import logging
from typing import Callable

from tcfbot.event import EventList
from tcfbot.account import Account, AccountList
from tcfbot.bot import Bot
from tcfbot.bot_crawler import CrawlerBot
from tcfbot.reservation import Reservation
from tcfbot.payment_day import PaymentDayList
from tcfbot.database import Database
import threading

# logger
logger = logging.getLogger(__file__)


class Engine:
    def __init__(self, **kwargs):
        """
            Core Worker Engine of tcfbot
            Fetches events from tcf website
        """
        self._account: Account = kwargs.get('account', Account())
        self.account_list: AccountList = kwargs.get('account_list', AccountList())
        self.database: Database = kwargs.get('database', Database())
        self.rate_limit: int = kwargs.get('rate_limit', 1500) % 10000
        self.max_bots: int = kwargs.get('max_bots', 10)
        self.bot_count: int = 0
        self.account_count: int = 0
        self.sleep_time: int = kwargs.get('sleep_time', 5) % 100
        self.crawler_bot: CrawlerBot = None
        self.abort: bool = False
        self.on_start: Callable = None
        self.on_stop: Callable = None
        self.running: bool = False
        self.on_reserve_account: Callable = None
        self.lock = threading.Lock()

    def __del__(self):
        pass

    def start(self):
        """
        start engine
        """
        self.account_count = 0
        self.abort = False
        self.create_crawler_bot()
        self.run_crawler_bot()
        self.trigger_engine_started()

    def stop(self):
        self.abort = False

    def trigger_engine_started(self):
        self.running = True
        if self.on_start:
            self.on_start(self)

    def trigger_engine_stopped(self):
        self.running = False
        if self.on_stop:
            self.on_stop(self)

    def trigger_account_reserved(self, reservation: Reservation):
        if self.on_reserve_account:
            self.on_reserve_account(self, reservation)

    def create_crawler_bot(self):
        self.crawler_bot = CrawlerBot(event_crawler_callback=self.crawler_event_callback,
                                      payment_day_crawler_callback=self.crawler_payment_callback,
                                      rate_limit=self.rate_limit,
                                      account=self._account)

    def bot_callback(self, sender, error, data):
        if error:
            logger.error(error.get('message'))
            if error.get('error') == 'login':
                logger.warning(f'removing invalid account "{sender.account.email}" from list')
                self.account_list.remove_account(sender.account)
            elif error.get('error') == 'reserve':
                logger.warning(f'reservation for "{sender.account.email}" failed')
            else:
                assert False, "Unexpected error"
        else:
            logger.warning(data.get('message'))
            reservation = data.get('reservation')
            # sync data to database
            self.sync_account_to_database(sender.account)
            self.sync_reservation_to_database(reservation)
            # trigger reservation done
            self.trigger_account_reserved(reservation)

        if not self.abort and \
                self.account_count < self.account_list.count():
            self.next_account(sender)
        else:
            self.bot_count -= 1
        # all bots completed
        if self.bot_count == 0:
            self.account_count = 0
            if not self.abort:
                logger.warning('All bots completed')
                self.remove_reserved_accounts()
                logger.warning(f'sleeping for {self.sleep_time} seconds before running event crawler')
                time.sleep(self.sleep_time)
                self.crawler_bot.run_event_crawler()
            else:
                self.trigger_engine_stopped()

    def next_account(self, bot: Bot):
        bot.account = self.account_list.get_item(self.account_count)
        self.account_count += 1
        logger.warning(f'taking reservation for account:{bot.account.email}')
        bot.run()

    def run_crawler_bot(self):
        """
        start crawler bot
        """
        self.crawler_bot.run_event_crawler()

    def crawler_event_callback(self, sender, error, data):
        if error:
            # log message
            logger.error(error.get('message'))
            if self.abort:
                return self.trigger_engine_stopped()
            # login failure
            if error.get('error') == 'LoginError':
                logger.warning("Invalid account")
            elif error.get('error') == 'NotLoggedInError':
                # clear session
                sender.clear_session()
            logger.warning(f'sleeping for {self.sleep_time} seconds')
            time.sleep(self.sleep_time)
            self.run_crawler_bot()
        else:
            logger.warning(data.get('message'))
            event_list = data.get('event_list')
            logger.warning(f'fetched {event_list.count()} events')
            #assert event_list.count() > 0, "Empty event list"

            open_event_list = event_list.get_open_events()

            self.sync_events_to_database(event_list)

            logger.warning(f'{open_event_list.count()} open events')
            # fetch payments now
            if self.abort:
                return self.trigger_engine_stopped()
            if open_event_list.count() > 0:
                logger.warning('got open events, crawling payment days')
                sender.run_payment_crawler(open_event_list)
            else:
                logger.warning(f'sleeping for {self.sleep_time} seconds')
                time.sleep(self.sleep_time)
                self.run_crawler_bot()

    def crawler_payment_callback(self, sender, error, data):
        if error:
            # log message
            logger.error(error.get('message'))
            if self.abort:
                return self.trigger_engine_stopped()
            logger.warning(f'sleeping for {self.sleep_time} seconds')
            time.sleep(self.sleep_time)
            self.run_crawler_bot()
        else:
            if self.abort:
                return self.trigger_engine_stopped()
            logger.warning('got data payments')
            payment_day_list = data.get('payment_day_list')
            event_list = data.get('event_list')

            #assert event_list.count() > 0, "Empty event list"
            #assert payment_day_list.count() > 0, "Empty payment days"
            if payment_day_list.count() > 0:
                self.sync_payment_days_to_database(payment_day_list)

                logger.warning('reserve accounts')
                self.reserve_accounts(event_list, payment_day_list)
            else:
                logger.warning(f'sleeping for {self.sleep_time} seconds')
                time.sleep(self.sleep_time)
                self.run_crawler_bot()

    def reserve_accounts(self, event_list: EventList, payment_day_list: PaymentDayList):
        while self.bot_count < self.max_bots and \
                self.bot_count < self.account_list.count() and \
                self.account_count < self.account_list.count():
            account = self.account_list.get_item(self.account_count)
            self.account_count += 1
            if not account.reserved:
                logger.warning(f'taking reservation for account:{account.email}')
                bot = Bot(account=account,
                          rate_limit=self.rate_limit,
                          events=event_list,
                          payment_days=payment_day_list,
                          callback=self.bot_callback,
                          lock=self.lock)
                self.bot_count += 1
                bot.run()
                time.sleep(self.rate_limit / 10)
        # if no bot was launched
        if self.bot_count == 0:
            logger.warning('No account was scheduled for reservation')
            if not self.abort:
                logger.warning(f'Sleeping for {self.sleep_time} seconds before launching event crawler')
                time.sleep(self.sleep_time)
                self.crawler_bot.run_event_crawler()
            else:
                self.trigger_engine_stopped()

    def remove_reserved_accounts(self):
        """
        removes already reserved accounts
        """
        for account in self.account_list:
            if account.reserved:
                logger.warning(f'Removing account with mail: {account.email} because it\'s already reserved')
                self.account_list.remove_account(account)

    def sync_events_to_database(self, event_list: EventList):
        """
        sync fetched events to database
        """
        for event in event_list:
            if self.database.event_exists(event):
                self.database.update_event(event)
            else:
                self.database.insert_event(event)
        self.database.commit()

    def sync_payment_days_to_database(self, payment_list: PaymentDayList):
        """
        sync fetched payment days to database
        """
        for payment_day in payment_list:
            if self.database.payment_day_exists(payment_day):
                self.database.update_payment_day(payment_day)
            else:
                self.database.insert_payment_day(payment_day)
        self.database.commit()

    def sync_reservation_to_database(self, reservation: Reservation):
        """
        sync reservation to database
        """
        self.database.insert_reservation(reservation)
        self.database.commit()

    def sync_account_to_database(self, account: Account):
        """
        sync account to database
        """
        if self.database.account_exists(account):
            self.database.update_account(account)
        else:
            self.database.insert_account(account)
        self.database.commit()

    def get_running(self) -> bool:
        return self.running
