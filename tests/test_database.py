from tcfbot.database import Database
from tcfbot.account import Account
from tcfbot.event import Event
from tcfbot.payment_day import PaymentDay, PaymentDayList
from tcfbot.reservation import Reservation, ReservationList

import threading

db = Database('tcf_test.sqlite')
db.drop_tables()
db.create_tables()
db.init_data()

event = Event(antenna_name='alger', uid='6130d7adee43a',
              title='TCF Canada', antenna_id=1,
              local='alger', price='10000',
              status=1, full=1)
db.insert_event(event)

payment_day = PaymentDay(date_to="2021-05-02",
                         event_uid="6130d7adee43a",
                         date_from="2021-05-01",
                         time_shift_uid="6487497497",
                         time_shift_morning=True)



db.insert_payment_day(payment_day)
account = Account(email='lsldgl144@gmail.com', password='sdgdg')
db.insert_account(account)

reservation = Reservation(account=account,
                              payment_day=payment_day,
                              event=event)
db.insert_reservation(reservation)
print(db.reservation_exists(reservation))
print(db.get_reservations().json())


#print(db.payment_day_exists(payment_day))
#db.execute_query("""
#SELECT * FROM PAYMENT_DAYS;
#""")
#print(db.fetchall())

#payment_day.date_to = 'hello world'

#db.update_payment_day(payment_day)
#db.execute_query("""
#SELECT * FROM PAYMENT_DAYS;
#""")
#print(db.fetchall())
#db.delete_payment_day(payment_day)

#print(db.get_payment_days().json())

#account = Account(email='lsldgl144@gmail.com', password='sdgdg')
#db.insert_account(account)

#account = Account(email='lsldgl1g44@gmail.com', password='sdgdg')
#account.reserved = 1
#db.insert_account(account)
#account.password = 'lyes'
#db.update_account(account)
#print(bool(db.account_exists(account)))


#db.delete_account(account)

#db.execute_query("""
#SELECT * FROM ACCOUNTS""")
#print(db.fetchall())
#db.execute_query("""
#SELECT * FROM EXAMS""")
#print(db.fetchall())

#print(db.get_accounts().json())

event = Event(antenna_name='alger', uid='6130d7adee43a',
              title='TCF Canada', antenna_id=1,
              local='alger', price='10000',
              status=1, full=1)
db.insert_event(event)

event = Event(antenna_name='alger', uid='6130d8adee43a',
              title='TCF SO', antenna_id=3,
              local='alger', price='10000',
              status=1, full=1)
db.insert_event(event)

print(db.execute_query("SELECT * FROM EVENTS").fetchall())
print(db.get_events().json())

db.update_event(event)

db.commit()
db.close()