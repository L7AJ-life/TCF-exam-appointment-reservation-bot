"""
command interface
"""
from tcfbot.account import Account, AccountList
from tcfbot.controller import Controller
from tcfbot.engine import Engine
from tcfbot.event import EventList
from tcfbot.payment_day import PaymentDayList
from tcfbot.reservation import ReservationList


class Command:
    def __init__(self, **kwargs):
        """
        constructor
        """
        self.controller: Controller = kwargs.get('controller', Controller())

    def engine_stopped_reload_config(self, engine: Engine):
        """
        on_stopped reload config
        """
        if engine is self.controller.engine:
            self.controller.config.load_config()
            self.controller.configure_engine()
            self.controller.start_engine()
            engine.on_stop = None

    def engine_stopped_reload_accounts(self, engine: Engine):
        """
        on_stopped reload accounts
        """
        if engine is self.controller.engine:
            self.controller.load_accounts()
            self.controller.start_engine()
            engine.on_stop = None

    def reload_config(self):
        """
        reloads config settings
        """
        self.controller.engine.on_stop = self.engine_stopped_reload_config
        self.controller.stop_engine()

    def reload_accounts(self):
        """
        reload accounts from database
        """
        self.controller.engine.on_stop = self.engine_stopped_reload_accounts
        self.controller.stop_engine()

    def insert_account(self, email: str, password: str, motivation: int = 1,
                       antenna: int = 1, exam: int = 1):
        """
        insert new account to database
        """
        self.controller.database.insert_account(Account(email=email,
                                                        password=password,
                                                        reserved=0,
                                                        motivation=motivation,
                                                        exam=exam,
                                                        antenna=antenna))

    # methods below might be used as this example
    # to get json data
    # return json.dumps(command.get_events().json())
    def get_events(self) -> EventList:
        """
        returns EventList object
        """
        return self.controller.database.get_events()

    def get_accounts(self) -> AccountList:
        """
        returns AccountList object
        """
        return self.controller.database.get_accounts()

    def get_reservations(self) -> ReservationList:
        """
        get reservation list
        """
        return self.controller.database.get_reservations()

    def get_payment_days(self) -> PaymentDayList:
        """
        get payment days list
        """
        return self.controller.database.get_payment_days()

    def stop_engine(self):
        """
        stops engine
        """
        if self.controller.engine.get_running():
            self.controller.stop_engine()
        else:
            # maybe raising en exception is better
            return "already stopped"

    def start_engine(self):
        """
        stops engine
        """
        if not self.controller.engine.get_running():
            self.controller.start_engine()
        else:
            # maybe raising en exception is better
            return "already started"
