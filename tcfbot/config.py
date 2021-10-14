"""
config loader
"""

from typing import Dict, Any
import ujson as json
import logging
from tcfbot.account import Account

# logger
logger = logging.getLogger(__file__)


class Config:
    def __init__(self, **kwargs):
        """
        constructor
        """
        self.file_name: str = kwargs.get('file_name', 'config.json')
        self.config: Dict[str, Any] = dict()

    def load_config(self) -> None:
        """
        read config from json file
        """
        try:
            fp = open(self.file_name, 'r')
            self.config = json.load(fp)
            fp.close()
        except Exception as e:
            logger.warning(f'exception occurred while loading config: {e}')

    def get_account(self) -> Account:
        """
        returns Account object
        """
        account = self.config.get('account', {})
        return Account(email=account.get('email', ''),
                       password=account.get('password', ''))

    def get_telegram_token(self) -> str:
        """
        returns telegram bot token
        """
        return self.config.get('telegram', {}).get('token', '')

    def get_telegram_chat_id(self) -> str:
        """
        return telegram chat_id
        """
        return self.config.get('telegram', {}).get('chat_id', '')

    def get_engine_max_bots(self) -> int:
        """
        return engine max bots count
        """
        return self.config.get('engine', {}).get('max_bots', 10)

    def get_engine_sleep_time(self):
        """
        return sleep time in seconds
        """
        return self.config.get('engine', {}).get('sleep_time_sec', 5)

    def get_engine_rate_limit(self):
        """
        returns rate limit in millisecond
        """
        return self.config.get('engine', {}).get('rate_limit_ms', 500)
