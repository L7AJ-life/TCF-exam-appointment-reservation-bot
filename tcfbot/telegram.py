"""
telegram C&C
"""

from tcfbot.command import Command
from tcfbot.engine import Engine

import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
logger = logging.getLogger(__name__)


class Telegram(Command):

    def __init__(self, **kwargs):
        super.__init__(super)
        self.token: str = kwargs.get('token', self.controller.config.get_telegram_token())
        self.chat_id: str = kwargs.get('chat_id', self.controller.config.get_telegram_chat_id())

    def on_start_callback(self, sender: Engine):
        pass

    def start(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        if self.controller.engine.get_running():
            update.message.reply_markdown_v2(
                'Already started!',
                reply_markup=ForceReply(selective=True),
            )
        else:
            self.controller.configure_engine()
            self.controller.engine.on_start = self.on_start_callback
            self.controller.start_engine()

    def main(self) -> None:
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        updater = Updater(self.token)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        dispatcher.add_handler(CommandHandler("start", self.start))
        #dispatcher.add_handler(CommandHandler("help", help_command))

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()