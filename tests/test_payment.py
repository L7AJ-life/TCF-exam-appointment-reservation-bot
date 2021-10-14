from tcfbot.payment_day import PaymentDay, PaymentDayList

payment_day = PaymentDay(date_to="2021-05-02",
                         event_uid="qf4q68bc486",
                         date_from="2021-05-01",
                         time_shift_uid="6487497497",
                         time_shift_morning=True)

print(payment_day.text())
print(payment_day.json())

payment_day_list = PaymentDayList()
payment_day_list.add_payment_day(payment_day)

print(payment_day_list.json())

for payment_day in payment_day_list:
    print(payment_day.text())

payment_day_list.delete_payment_day(payment_day)
