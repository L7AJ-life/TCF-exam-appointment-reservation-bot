from typing import Any, List
import sqlite3
import logging
from tcfbot.account import Account, AccountList
from tcfbot.event import Event, EventList
from tcfbot.payment_day import PaymentDay, PaymentDayList
from tcfbot.reservation import Reservation, ReservationList

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path='tcf.sqlite'):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def create_tables(self) -> None:
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS 
                ANTENNAS (
                    antenna_id INT NOT NULL,
                    antenna_name VARCHAR NOT NULL,
                    PRIMARY KEY (antenna_id)
                )
            ;
        """)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS 
                EXAMS (
                    exam_id INT NOT NULL,
                    exam_name VARCHAR NOT NULL,
                    PRIMARY KEY (exam_name)
                )
            ;
        """)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS 
                MOTIVATIONS (
                    motivation_id INT,
                    motivation_name VARCHAR NOT NULL,
                    PRIMARY KEY (motivation_id)
                )
            ;
        """)

        self.execute_query("""
            CREATE TABLE IF NOT EXISTS 
                ACCOUNTS (
                    account_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR NOT NULL UNIQUE,
                    password VARCHAR NOT NULL,
                    reserved INT NOT NULL,
                    antenna_id INT NOT NULL,
                    exam_id  INT NOT NULL,
                    motivation_id INT NOT NULL,
                    FOREIGN KEY(exam_id)
                        REFERENCES EXAMS(exam_id),
                    FOREIGN KEY (antenna_id)
                        REFERENCES ANTENNAS(antenna_id),
                    FOREIGN KEY(motivation_id)
                        REFERENCES MOTIVATIONS(motivation_id)
                )
            ;
        """)

        self.execute_query("""
            CREATE TABLE IF NOT EXISTS 
                EVENTS (
                    event_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    uid VARCHAR NOT NULL UNIQUE,
                    title VARCHAR NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    local TEXT NOT NULL,
                    status INT NOT NULL DEFAULT 0,
                    full   INT NOT NULL DEFAULT 0,
                    antenna_id INT NOT NULL,
                    exam_id INT NOT NULL,
                    FOREIGN KEY (antenna_id)
                        REFERENCES ANTENNAS(antenna_id),
                    FOREIGN KEY (exam_id)
                        REFERENCES EXAMS(exam_id)
                )
            ;
        """)

        self.execute_query("""
            CREATE TABLE IF NOT EXISTS 
                RESERVATIONS (
                    reservation_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    payment_id INTEGER NOT NULL,
                    account_id INT NOT NULL,
                    event_id INT NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES EVENTS(event_id),
                    FOREIGN KEY (account_id) REFERENCES ACCOUNTS(account_id),
                    FOREIGN KEY (payment_id) REFERENCES PAYMENT_DAYS(payment_id)
                )
            ;
        """)

        self.execute_query("""
            CREATE TABLE IF NOT EXISTS 
                PAYMENT_DAYS (
                    payment_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    date_from varchar NOT NULL,
                    date_to varchar NOT NULL,
                    time_shift_uid varchar NOT NULL UNIQUE,
                    time_shift_morning varchar NOT NULL,
                    event_id INT NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES EVENTS(event_id)
                )
            ;
        """)

    def init_data(self) -> None:
        """
        insert constant data
        """
        self.execute_query("""
            INSERT INTO 
                ANTENNAS         
            VALUES (1, 'Alger'),
                (2, 'Oran'),
                (3, 'Annaba'),
                (4, 'Constantine'),
                (5, 'Tlemcen')
            ;
        """)

        self.execute_query("""
            INSERT INTO 
                MOTIVATIONS 
            VALUES (1, 'Etudes en France'),
                (3, 'Immigration au Canada'),
                (4, 'Procedure de naturalisation'),
                (5, 'Autre')
            ;
        """)

        self.execute_query("""
            INSERT INTO 
                EXAMS 
            VALUES (1, 'TCF SO'),
                (2, 'TCF Canada'),
                (3, 'TCF dans le cadre de la DAP')
            ;
        """)

    def execute_query(self, sql_query: str) -> Any:
        """
        Execute sql query
        """
        try:
            return self.cursor.execute(sql_query)
        except Exception as e:
            logger.error(f'execute_query failed : {e}')

    def drop_tables(self):
        """
        Drop all database table
        """
        self.execute_query("""
            DROP TABLE 
                ACCOUNTS
            ;
        """)
        self.execute_query("""
            DROP TABLE 
                EVENTS
            ;
        """)
        self.execute_query("""
            DROP TABLE 
                EXAMS
            ;
        """)
        self.execute_query("""
            DROP TABLE 
                PAYMENT_DAYS
            ;
        """)
        self.execute_query("""
            DROP TABLE 
                RESERVATIONS
            ;
        """)
        self.execute_query("""
            DROP TABLE 
                ANTENNAS
            ;
        """)
        self.execute_query("""
            DROP TABLE 
                MOTIVATIONS
            ;
        """)

    def insert_account(self, account: Account):
        """Insert account to database"""
        self.execute_query(f"""
            INSERT INTO 
                ACCOUNTS (email, 
                    password,  
                    antenna_id, 
                    exam_id, 
                    motivation_id, 
                    reserved
                ) 
                VALUES ('{account.email}',
                    '{account.password}',
                    {account.antenna},
                    {account.exam},
                    {account.motivation},
                    {account.reserved}
                )
            ;
        """)

    def account_exists(self, account: Account) -> bool:
        """
        check if account is stored in database
        """
        try:
            return bool(self.execute_query(f"""
                SELECT 
                    EXISTS(
                        SELECT
                            *
                        FROM
                            ACCOUNTS
                        WHERE
                            email='{account.email}'
                    )
                ;
            """).fetchall()[0][0])
        except Exception as e:
            logger.error(f'Exception at account_exists: {e}')
        return False

    def update_account(self, account: Account) -> None:
        """update account in database"""
        self.execute_query(f"""
                UPDATE ACCOUNTS
                SET
                    password='{account.password}',
                    antenna_id={account.antenna}, 
                    exam_id={account.exam},
                    motivation_id={account.motivation}, 
                    reserved={account.reserved}
                WHERE
                    email='{account.email}'
                ;
                """)

    def delete_account(self, account: Account) -> None:
        """delete account from database"""
        self.execute_query(f"""
            DELETE FROM 
                ACCOUNTS
            WHERE
                email='{account.email}'
            ;
        """)

    def get_accounts(self) -> AccountList:
        """
        returns AccountList object
        containing saved accounts
        data from sqlite database
        """
        account_list = AccountList()
        for row in self.execute_query(f"""
            SELECT
                email, 
                password,  
                antenna_id, 
                exam_id, 
                motivation_id, 
                reserved
            FROM
                ACCOUNTS
            ;
                """).fetchall():
            account = Account(email=row[0], password=row[1],
                              antenna=row[2], exam=row[3],
                              motivation=row[4], reserved=row[5])
            account_list.add_account(account)

        return account_list

    def insert_event(self, event: Event) -> None:
        """
        Inserts an event to database
        """
        self.execute_query(f"""
            INSERT INTO 
                EVENTS (uid,
                    title,
                    price,
                    local,
                    status,
                    full,
                    antenna_id,
                    exam_id
                )
                VALUES ("{event.uid}",
                    "{event.title}",
                    {event.price},
                    "{event.local}",
                    {event.status},
                    {event.full},
                    {event.antenna_id},
                    (SELECT exam_id FROM EXAMS WHERE exam_name="{event.title}")
                )
            ;
        """)

    def event_exists(self, event: Event) -> bool:
        """
            check if event is stored in database
        """
        try:
            return bool(self.execute_query(f"""
                    SELECT 
                        EXISTS(
                            SELECT
                                *
                            FROM
                                EVENTS
                            WHERE
                                uid='{event.uid}'
                        )
                    ;
                    """).fetchall()[0][0])
        except Exception as e:
            logger.error(f'Exception at event_exists: {e}')
        return False

    def update_event(self, event: Event) -> None:
        """update event in database"""
        self.execute_query(f"""
                UPDATE 
                    EVENTS
                SET
                    title="{event.title}",
                    price="{event.price}",
                    local="{event.local}",
                    status={event.status},
                    full={event.full},
                    antenna_id={event.antenna_id},
                    exam_id=(
                        SELECT 
                            exam_id 
                        FROM 
                            EXAMS 
                        WHERE 
                            exam_name="{event.title}")
                WHERE
                    uid='{event.uid}'
                ;
                """)

    def delete_event(self, event: Event) -> None:
        """delete account from database"""
        self.execute_query(f"""
            DELETE FROM 
                EVENTS
            WHERE
                uid='{event.uid}';
            """)

    def get_events(self) -> EventList:
        """
        fetch events from data base
        """
        event_list = EventList()
        for row in self.execute_query("""
                    SELECT 
                        e.uid,
                        e.title,
                        e.price,
                        e.local,
                        e.status,
                        e.full,
                        a.antenna_name,
                        e.antenna_id
                    FROM
                        EVENTS e
                            INNER JOIN
                        ANTENNAS a
                            ON e.antenna_id = a.antenna_id
                    ; 
                    """).fetchall():
            event = Event(uid=row[0], title=row[1], price=row[2],
                          local=row[3], status=row[4], full=row[5],
                          antenna_name=row[6], antenna_id=row[7])
            event_list.add_event(event)

        return event_list

    def insert_payment_day(self, payment_day: PaymentDay) -> None:
        """insert payment day to database"""
        self.execute_query(f"""
            INSERT INTO 
                PAYMENT_DAYS(date_from,
                        date_to,
                        time_shift_uid,
                        time_shift_morning,
                        event_id)
                VALUES('{payment_day.date_from}', 
                    '{payment_day.date_to}',
                    '{payment_day.time_shift_uid}',
                    '{payment_day.time_shift_morning}',
                    (
                        SELECT
                            event_id
                        FROM
                            EVENTS
                        WHERE
                            uid='{payment_day.event_uid}'       
                    )
                )
            ;
        """)

    def payment_day_exists(self, payment_day: PaymentDay) -> bool:
        """
        check if payment_day exists
        """
        try:
            return bool(self.execute_query(f"""
            SELECT 
                EXISTS(
                    SELECT 
                        *
                    FROM
                        PAYMENT_DAYS
                    WHERE
                        time_shift_uid='{payment_day.time_shift_uid}'   
                )
            ;
            """).fetchall()[0][0])
        except Exception as e:
            logger.error(f"payment_day_exists failed: {e}")
        return False

    def update_payment_day(self, payment_day: PaymentDay) -> None:
        """
        update payment day
        """
        self.execute_query(f"""
            UPDATE 
                PAYMENT_DAYS
            SET
                date_from = '{payment_day.date_from}', 
                date_to   = '{payment_day.date_to}',
                time_shift_morning = '{payment_day.time_shift_morning}', 
                event_id  = (
                                SELECT
                                    event_id
                                FROM
                                    EVENTS
                                WHERE
                                    uid='{payment_day.event_uid}'
                            )
            WHERE
                time_shift_uid='{payment_day.time_shift_uid}'
            ;
        """)

    def delete_payment_day(self, payment_day: PaymentDay) -> None:
        """
        delete payment_day from database
        """
        self.execute_query(f"""
            DELETE FROM
                PAYMENT_DAYS
            WHERE
                time_shift_uid='{payment_day.time_shift_uid}'
            ;
        """)

    def get_payment_days(self) -> PaymentDayList:
        """
        fetch stored payment days
        and return PaymentDayList Object
        """
        payment_day_list = PaymentDayList()
        for row in self.execute_query("""
                SELECT 
                    p.date_to,
                    p.date_from,
                    p.time_shift_uid,
                    p.time_shift_morning,
                    e.uid
                FROM
                    PAYMENT_DAYS p
                        INNER JOIN
                    EVENTS e
                        ON e.event_id=p.event_id
                ;
                """).fetchall():
            payment_day = PaymentDay(date_to=row[0], date_from=row[1],
                                     time_shift_uid=row[2],
                                     time_shift_morning=row[3],
                                     event_uid=row[4])
            payment_day_list.add_payment_day(payment_day)

        return payment_day_list

    def insert_reservation(self, reservation: Reservation):
        """
        Insert reservation to database
        """
        self.execute_query(f"""
            INSERT INTO
                RESERVATIONS(
                    account_id,
                    event_id,
                    payment_id
                )
                VALUES(
                    (
                        SELECT
                            account_id
                        FROM
                            ACCOUNTS
                        WHERE
                            email='{reservation.account.email}'
                    ),
                    (
                        SELECT
                            event_id
                        FROM
                            EVENTS
                        WHERE
                            uid='{reservation.event.uid}'
                    ),
                    (
                        SELECT
                            payment_id
                        FROM
                            PAYMENT_DAYS
                        WHERE
                            time_shift_uid='{reservation.payment_day.time_shift_uid}'
                    )
                )
            ;
        """)

    def reservation_exists(self, reservation: Reservation) -> bool:
        try:
            return bool(self.execute_query(f"""
                    SELECT
                        EXISTS(
                            SELECT
                                *
                            FROM 
                                RESERVATIONS
                            WHERE
                                account_id=(
                                            SELECT
                                                account_id
                                            FROM
                                                ACCOUNTS
                                            WHERE
                                                email='{reservation.account.email}'
                                           )
                            AND
                                event_id  =(
                                            SELECT
                                                event_id
                                            FROM
                                                EVENTS
                                            WHERE
                                                uid='{reservation.event.uid}'
                                           )
                            AND
                                payment_id=(
                                            SELECT
                                                payment_id
                                            FROM
                                                PAYMENT_DAYS
                                            WHERE
                                                time_shift_uid='{reservation.payment_day.time_shift_uid}'   
                                           )     
                        )
                    ;
                """).fetchall()[0][0])
        except Exception as e:
            logger.error(f"reservation_exists failed: {e}")
        return False

    def delete_reservation(self, reservation: Reservation):
        self.execute_query(f"""
            DELETE FROM
                RESERVATIONS
            WHERE
                account_id=(
                            SELECT
                                account_id
                            FROM
                                ACCOUNTS
                            WHERE
                                email='{reservation.account.email}'
                            )
            AND
                event_id=(
                            SELECT
                                event_id
                            FROM
                                EVENTS
                            WHERE
                                uid='{reservation.event.uid}'
                           )
            AND
                payment_id=(
                            SELECT
                                payment_id
                            FROM
                                PAYMENT_DAYS
                            WHERE
                                time_shift_uid='{reservation.payment_day.time_shift_uid}'   
                           )     
                
            ;
        """)

    def get_reservations(self) -> ReservationList:
        """
        fetch reservations from database
        return ReservationList object
        """
        reservation_list = ReservationList()
        for reservation_row in self.execute_query("""
                    SELECT
                        account_id,
                        event_id,
                        payment_id
                    FROM
                        RESERVATIONS
                    ;
                """).fetchall():
            account_row = self.execute_query(f"""
                            SELECT
                                email, 
                                password,  
                                antenna_id, 
                                exam_id, 
                                motivation_id, 
                                reserved
                            FROM
                                ACCOUNTS
                            WHERE
                                account_id={reservation_row[0]}
                            ; 
                        """).fetchall()[0]
            account = Account(email=account_row[0], account_row=account_row[1],
                              antenna=account_row[2], exam=account_row[3],
                              motivation=account_row[4], reserved=account_row[5])

            event_row = self.execute_query(f"""
                    SELECT 
                        e.uid,
                        e.title,
                        e.price,
                        e.local,
                        e.status,
                        e.full,
                        a.antenna_name,
                        e.antenna_id
                    FROM
                        EVENTS e
                            INNER JOIN
                        ANTENNAS a
                            ON e.antenna_id = a.antenna_id
                    WHERE
                        e.event_id={reservation_row[1]}
                    ;                
                """).fetchall()[0]
            event = Event(uid=event_row[0], title=event_row[1], price=event_row[2],
                          local=event_row[3], status=event_row[4], full=event_row[5],
                          antenna_name=event_row[6], antenna_id=event_row[7])

            payments_row = self.execute_query(f"""
                            SELECT 
                                p.date_to,
                                p.date_from,
                                p.time_shift_uid,
                                p.time_shift_morning,
                                e.uid
                            FROM
                                PAYMENT_DAYS p
                                    INNER JOIN
                                EVENTS e
                                    ON e.event_id=p.event_id
                            WHERE
                                p.payment_id={reservation_row[2]}
                            ;          
                        """).fetchall()[0]
            payment_day = PaymentDay(date_to=payments_row[0], date_from=payments_row[1],
                                     time_shift_uid=payments_row[2],
                                     time_shift_morning=payments_row[3],
                                     event_uid=payments_row[4])

            reservation = Reservation(account=account,
                                      event=event,
                                      payment_day=payment_day)

            reservation_list.add_reservation(reservation)

        return reservation_list

    def fetchall(self) -> List[Any]:
        """fetch query execution data"""
        return self.cursor.fetchall()

    def commit(self) -> None:
        """
        commit changes to database
        """
        self.connection.commit()

    def close(self):
        """
        close connection to database
        """
        self.connection.close()
