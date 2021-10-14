"""
engine controller
"""

from tcfbot.engine import Engine
from tcfbot.database import Database
from tcfbot.account import Account, AccountList
from tcfbot.config import Config


class Controller:
    def __init__(self, **kwargs):
        """
        constructor
        """
        self.database: Database = kwargs.get('database', Database())
        self.engine: Engine = kwargs.get('engine', Engine(database=self.database))
        self.config: Config = kwargs.get('config', Config())
        #self.database.create_tables()
        #self.database.init_data()

    def start_engine(self):
        """
        start the engine
        """
        self.engine.start()

    def stop_engine(self):
        """
        stop the engine
        """
        self.engine.stop()

    def load_accounts(self):
        """
        load account list from database
        """
        self.engine.account_list = self.database.get_accounts()

    def configure_engine(self):
        """
        set engine config settings
        """
        self.engine._account = self.config.get_account()
        self.engine.max_bots = self.config.get_engine_max_bots()
        self.engine.sleep_time = self.config.get_engine_sleep_time()
        self.engine.rate_limit = self.config.get_engine_rate_limit()
