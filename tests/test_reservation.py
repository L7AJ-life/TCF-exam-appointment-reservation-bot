from tcfbot.reservation import Reservation, ReservationList
from tcfbot.account import Account
from tcfbot.event import Event
from tcfbot.payment_day import PaymentDay

reservation = Reservation(account=Account(email='lsldgl144@gmail.com',
                                          password='sdgdg'),
                          event=Event(antenna_name='alger', uid='6130d7adee43a',
                                      title='TCF SO', antenna_id=1,
                                      local='alger', price='10000',
                                      status=1, full=1),
                          payment_day=PaymentDay(date_to="2021-05-02",
                                                 event_uid="qf4q68bc486",
                                                 date_from="2021-05-01",
                                                 time_shift_uid="6487497497",
                                                 time_shift_morning=True)
                         )

print(reservation.text())

print(reservation.json())
rl = ReservationList()
rl.add_reservation(reservation)
for reservation in rl:
    print(reservation.text())