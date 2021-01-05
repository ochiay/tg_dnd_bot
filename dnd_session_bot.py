#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, context):
    """Send a message when the command /start is issued"""
    update.message.reply_text("Dark cycles, sunlander")

def help(update, context):
    """Send a help message when the command /help is issued"""
    update.message.reply_text("This bot still do nothing")

def main():
    """Start bot"""
    updater = Updater("1386831448:AAEGITEUsVitfTgvRUEj0RDhGfGO2G7yvo0", use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
