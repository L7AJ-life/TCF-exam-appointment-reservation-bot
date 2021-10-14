from tcfbot.account import Account, AccountList
import rapidjson as json

acc = Account(email='lsldgl144@gmail.com', password='sdgdg')

print(json.dumps(acc.json()))
print(acc.text())

al = AccountList()


print('add_account', al.add_account(acc))
print('save_to_file', al.save_to_file('C:\\Users\\s\\Desktop\\file.txt'))
#print('load_from_file', al.load_from_file('C:\\Users\\s\\Desktop\\file.txt'))
#print('load_from_file', al.load_from_file('C:\\Users\\s\\Desktop\\file.txt'))
#print('load_from_file', al.load_from_file('C:\\Users\\s\\Desktop\\file.txt'))
print('count', al.count())
#print('save_to_file', al.save_to_file('C:\\Users\\s\\Desktop\\file.txt'))

for account in al:
    print(account.text())

al.sort()
#al.print()
print('remove_duplicates', al.remove_duplicates())
#al.print()

print('count', al.count())
print('find_by_mail', al.find_by_mail('lsldgl144@gmail.com'))
print('delete_account_at_index', al.delete_account_at_index(al.find_by_mail('lsldgl144@gmail.com')))
