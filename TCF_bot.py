#/usr/bin/python3

from tcfbot.controller import Controller
#from tcfbot.account import AccountList
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# logger
logger = logging.getLogger(__file__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)



def main() -> None:
    """
    how to use C&C with API

    forom tcfbot.command import Command
    # set created controller after starting engine
    # means After try except blocks
    # where you start uvicorn server
    command = Command(controller=conroller)

    # read command file to see supported actions
    """
    #account_list = AccountList()
    #account_list.load_from_file(sys.argv[1])

    controller = Controller()
    controller.load_accounts()
    controller.config.file_name = 'config.json'
    controller.config.load_config()
    #controller.engine.account_list = account_list
    try:
        controller.configure_engine()
        controller.start_engine()
    except Exception as e:
        print(f'Exception occurred {e}')


if __name__ == '__main__':
    main()
