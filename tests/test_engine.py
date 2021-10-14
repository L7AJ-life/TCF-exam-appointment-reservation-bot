from tcfbot.database import Database
from tcfbot.account import Account, AccountList
from tcfbot.engine import Engine

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import logging
logging.basicConfig(level=logging.INFO)


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

db = Database('tcf_test.sqlite')
db.drop_tables()
db.create_tables()
db.init_data()

acc1 = Account(email='lsldgl144@gmail.com', password='sdgdg')
acc2 = Account(email='lyes.fdfdgdfg@gmail.com', password='#sdfgdsgdsg')
al = AccountList()
al.add_account(acc2)
al.add_account(acc1)

e = Engine(account=acc2,
           rate_limit=999,
           database=db,
           account_list=al,
           max_bots=10,
           sleep_time=5)

e.start()
