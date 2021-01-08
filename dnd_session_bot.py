#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import re
import logging


from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TG_TOKEN = '1428831437:AAG_bw6SipdV0affAUnpj-7vBPY0FYUET18'
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued"""
    update.message.reply_text("Dark cycles, sunlander")


def help(update: Update, context: CallbackContext):
    """Send a help message when the command /help is issued"""
    update.message.reply_text(
        "Commands:\n"
        "  /roll : <int>d<int>+<int>...+<int>\n"
        "  /help : output this message"
    )

#-------------------------------------------------------------------------------
def roll(update:Update, context: CallbackContext):
    """roll dice
    /roll <a:int>d<b:int>+<modifier[0]:int>...+<modifier[n]int>
        a, b : floor and ceiling for random.randint
        modifier(_sum) : variable for storing "+int" values
    """

    # prepare string

    text = ''.join(context.args)
    regexp = re.compile('^(?P<dice>\\d+d\\d+)(?P<modifier>([\+-]\d+)*)?$');

    temporary = regexp.match(text)

    a, b = temporary['dice'].split('d')
    modifier = re.findall(r'([\+-]\d+)', temporary['modifier'])

    # roll the dice
    a,b = int(a), int(b)
    dice_roll = [random.randint(1, b) for _ in range(a)]

    # modifier sum
    modifier_sum = 0
    text_message = ""
    print(modifier)
    if modifier:
        for el in modifier: modifier_sum += int(el)
        text_message = f" + {modifier_sum}"

    # apply modifier
    result = sum(dice_roll) + modifier_sum

    dice_roll = ' + '.join(map(str, dice_roll))
    character_name = update.message.from_user.first_name
    text_message =\
        f"{character_name} выкидывает {result} :\n"\
        f"({a}d{b}){text_message} :\n({dice_roll}){text_message}"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_message)

#-------------------------------------------------------------------------------
def main():
    """Start bot"""
    updater = Updater(TG_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("roll", roll))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
