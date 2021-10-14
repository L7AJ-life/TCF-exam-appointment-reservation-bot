from tcfbot.account import Account
from tcfbot.database import Database

tcf_accounts = [
    ('fgdfgdfgdfg@gmail.com', 'dfgfdgfdg'),
]


tcf_accounts_dap = [
    ("fdgfdgfdg@gmail.com", "dfgfdgfdg")
]



db = Database()
db.drop_tables()
db.create_tables()
db.init_data()

for acc in tcf_accounts:
    account = Account(email=acc[0],
                      password=acc[1],
                      antenna=1,
                      reserved=0,
                      motivation=1,
                      exam=1)
    db.insert_account(account)

for acc in tcf_accounts_dap:
    account = Account(email=acc[0],
                      password=acc[1],
                      antenna=1,
                      reserved=0,
                      motivation=1,
                      exam=3)
    db.insert_account(account)

db.commit()
db.close()
