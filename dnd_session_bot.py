#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import re
import sqlite3
import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TG_TOKEN = '1428831437:AAG_bw6SipdV0affAUnpj-7vBPY0FYUET18'


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#-
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued"""

    #group = update.effective_chat.title

    update.message.reply_text("Dark cycles, sunlander.\n"
                              "Use /help to watch available operations")

#-
def dex(update:  Update, context: CallbackContext):


def help(update: Update, context: CallbackContext):
    """Send a help message when the command /help is issued"""
    update.message.reply_text(
        "Commands:\n"
        "  /set_name NAME [SURNAME]\n"
        "  /roll INTdINT [+INT+...+INT]\n"
        "  /help"
    )

#-

def connect_db(function):
    connection = None

    try:
        connection = sqlite3.connect("./dnd_session.db")
    except Error as e:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=e)
    connection.cursor()

    variables, variables = function();

    connection.execute(instruction, variables)
    connection.commit()
    connection.close()
    return wrapper


#-------------------------------------------------------------------------------
def set_name(update: Update, context: CallbackContext):
    connection = None
    try:
        connection = sqlite3.connect("./dnd_session.db")
    except Error as e:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=e)

    cursor = connection.cursor()

    id_user = id_group = first_name = second_name = 0
    try:
        id_user = update.effective_user.id
        id_group = update.effective_chat.id
        first_name = '"{}"'.format(context.args[0])
        second_name = '"{}"'.format(context.args[1]) if len(context.args) > 1 else '""'
    except IndexError:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="usage: /create_character NAME [SURNAME]")

    sql_instruction =\
        "REPLACE INTO character(id_user, id_group, first_name, second_name)"\
        "VALUES(%s, %s, %s, %s)"
    sql_variables = (id_user, id_group, first_name, second_name,)
    print("huyak")

    context.bot.send_message(
        chat_id=id_group,
        text=f"{first_name} {second_name}"
    )
    return ()
#-

def rename(update: Update, context: CallbackContext):
    pass
#-

def roll(update: Update, context: CallbackContext):
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

    if modifier:
        for el in modifier: modifier_sum += int(el)
        text_message = f" + {modifier_sum}"

    # apply modifier
    result = sum(dice_roll) + modifier_sum

    dice_roll = ' + '.join(map(str, dice_roll))
    character_name = update.message.from_user.first_name
    text_message =\
        f"{character_name} have rolled {result} :\n"\
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

    dp.add_handler(CommandHandler("set_name", set_name))
    dp.add_handler(CommandHandler("roll", roll))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
