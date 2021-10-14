"""
    Account class
    will contain informations about
    clients accounts
    cridentials , exams..etc
"""
import ujson as json
from typing import (Any, Dict, List)
from operator import attrgetter
import logging

logger = logging.getLogger(__name__)


class Account:
    def __init__(self, **kwargs):
        """
        Account constructor method
        @kwargs
        :email -> str
        :password -> str
        :motivation -> int (1, 3, 4, 5) default 1
            1 etude en france
            3 immigration au canada
            4 naturalization
            5 autre
        :antenna -> int (1, 2, 3, 4, 5) default 1
            1 alger
            2 oran
            3 annaba
            4 const
            5 tlemcen
        :exam -> int (1, 2, 3) default 1
            1 TCF SO
            2 TCF Canada
            3 DAP
        """
        self.email: str = kwargs.get('email', '')
        self.password: str = kwargs.get('password', '')
        self.motivation: int = kwargs.get('motivation', 1)
        self.antenna: int = kwargs.get('antenna', 1)
        self.exam: int = kwargs.get('exam', 1)
        self.reserved: bool = kwargs.get('reserved', 0)

    def __del__(self):
        del(self.email,
            self.password,
            self.exam,
            self.antenna,
            self.motivation)

    def json(self) -> Dict[str, Any]:
        """
        Account data as Dict (json like)
        """
        return {
            'email': self.email,
            'password': self.password,
            'motivation': self.motivation,
            'antenna': self.antenna,
            'exam': self.exam,
            'reserved': self.reserved
        }

    def text(self):
        return f"""Email: {self.email}
Password: {self.password}
Motivation: {self.motivation}
Antenna: {self.antenna}
Exam: {self.exam}
Reserved: {self.reserved}"""

# account list object


class AccountList:
    def __init__(self):
        """initialize list object"""
        self.__accounts: List[Account] = list()

    def __del__(self):
        """
        free memory
        """
        self.clear()
        del self.__accounts

    def load_from_file(self, file_name: str) -> bool:
        """
        Loads accounts from json file
        returns True on success
        False on error
        """
        try:
            fp = open(file_name, 'r')
            for account in json.load(fp).get('accounts', []):
                acc = Account()
                acc.email = account.get('email', '')
                acc.password = account.get('password', '')
                acc.motivation = account.get('motivation', 1)
                acc.antenna = account.get('antenna', 1)
                acc.exam = account.get('exam', 1)
                self.add_account(acc)
            fp.close()

            return True
        except Exception as e:
            logger.error(f"Exception in load_from_file: {e}")

        return False

    def save_to_file(self, filename) -> bool:
        """
        Saves current list of accounts to json file
        return True on success
        And False on exception
        """
        try:
            fp = open(filename, 'w')
            fp.write(json.dumps({
                'accounts': [acc.json() for acc in self.__accounts]
            }))
            fp.close()

            return True
        except Exception as e:
            logger.error(f"Exception in save_to_file: {e}")

        return False

    def clear(self) -> None:
        """
        clear list
        """
        return self.__accounts.clear()

    def remove_account(self, account: Account):
        """
         remove account from list
        """
        try:
            self.__accounts.remove(account)
            return True
        except Exception as e:
            logger.error(f'remove_account failed: {e}')
        return False

    def add_account(self, account: Account) -> bool:
        """
        Adds account to list
        """
        if type(account) == Account:
            self.__accounts.append(account)
            return True
        else:
            return False

    def count(self) -> int:
        return len(self.__accounts)

    def sort(self) -> None:
        """
        sort accounts objects by their email
        attribute to make it easy to
        remove duplicates
        """
        self.__accounts.sort(key=attrgetter('email'))

    def remove_duplicates(self) -> int:
        """
        Deletes duplicated accounts
        returns number found duplicates """
        self.sort()
        duplicates = 0
        try:
            for i in range(self.count()-1, 0, -1):
                if self.__accounts[i].email == self.__accounts[i-1].email:
                    self.__accounts.remove(self.__accounts[i])
                    duplicates += 1
            return duplicates
        except IndexError:
            logger.error('Invalid index error at remove_duplicates')
        except Exception as e:
            logger.error(f'Exception in remove_duplicates: {e}')

    def print(self) -> None:
        """prints all accounts as text"""
        for account in self.__accounts:
            print(account.text())

    def json(self) -> Dict[str, Any]:
        """
        returns JSON array of accounts aj json
        """
        try:
            return {
                'accounts': [acc.json() for acc in self.__accounts]
            }
        except Exception as e:
            logger.error(f'print_json failed: {e}')
        return {}

    def delete_account_at_index(self, index: int) -> bool:
        """
        deletes item at index
        returns True on success
        """
        try:
            self.__accounts.remove(self.__accounts[index])
            return True
        except Exception as e:
            logger.error(f'Exception in delete_account_at_index: {e}')

        return False

    def get_item(self, index: int) -> Account:
        if index < 0 or index >= self.count():
            raise Exception(f'get_item invalid index: {index}')

        return self.__accounts[index]

    def set_item(self, index: int, account: Account):
        if index < 0 or index >= self.count():
            raise Exception(f'set_item invalid index: {index}')

        if type(account) != Account:
            raise Exception(f'set_item unsupported type: {type(account)}')

        self.__accounts[index] = account

    def __iter__(self):
        """
        make object iterable
        """
        return AccountListIterator(self)


class AccountListIterator:
    def __init__(self, account_list: AccountList):
        self._account_list: AccountList = account_list
        self._index = 0

    def __next__(self):
        if self._index < self._account_list.count():
            result = self._account_list.get_item(self._index)
            self._index += 1
            return result
        raise StopIteration
