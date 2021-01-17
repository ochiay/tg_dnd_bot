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
#-------------------------------------------------------------------------------

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued"""

    #group = update.effective_chat.title

    update.message.reply_text("Dark cycles, sunlander.\n"
                              "Use /help to watch available operations")

#-------------------------------------------------------------------------------

def dex(update:  Update, context: CallbackContext):
    pass

#-------------------------------------------------------------------------------

def help(update: Update, context: CallbackContext):
    """Send a help message when the command /help is issued"""
    update.message.reply_text(
        "Commands:\n"
        "  /set_name NAME [SURNAME]\n"
        "  /roll INTdINT [+INT+...+INT]\n"
        "  /help"
    )

#-------------------------------------------------------------------------------

def connect_db(function):

    def wrapper(update: Update, context: CallbackContext):
        connection = None

        try:
            connection = sqlite3.connect("./dnd_session.db")
        except Error as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=e)
        #
        cursor = connection.cursor()

        try:
            function(update, context, cursor)
        except ValueError:
            print("vse` kon4ilos' huevo")
        connection.commit()
        connection.close()
        return function

    return wrapper

#-------------------------------------------------------------------------------

@connect_db
def me(update: Update, context: CallbackContext, cursor):
    id_user = id_group = first_name = second_name = 0
    try:
        id_user = update.effective_user.id
        id_group = update.effective_chat.id
        id_message = update.effective_message.message_id

    except IndexError:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="usage: /me")

    instruction =\
        """
        SELECT first_name, second_name FROM character
        WHERE id_user==? AND id_group==?;
        """
    variables = (id_user, id_group)
    cursor.execute(instruction, variables);
    character = cursor.fetchone();
    character = ' '.join([name for name in character if name])
    context.bot.send_message(
        chat_id = id_group,
        text = f"""You've remembered that you are {character}""",
        reply_to_message_id=id_message
    )
    return false

#-------------------------------------------------------------------------------

@connect_db
def set_name(update: Update, context: CallbackContext, cursor):
    """create or replace your character name.
    You have one character per session"""
    id_user = id_group = first_name = second_name = 0
    try:
        id_user = update.effective_user.id
        id_group = update.effective_chat.id
        first_name = f'{context.args[0]}'
        second_name = f'{context.args[1]}' if len(context.args) > 1 else None
    except IndexError:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="usage: /set_name NAME [SURNAME]")
        return True

    instruction =\
        '''
        REPLACE INTO character(id_user, id_group, first_name, second_name)
        VALUES(?, ?, ?, ?)
        '''

    variables = (id_user, id_group, first_name, second_name,)

    cursor.execute(instruction, variables)
    second_name = ' ' + second_name if second_name else ''
    answer = f'''{first_name}{second_name} was born'''
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = answer);

    return False

#-------------------------------------------------------------------------------

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

    dp.add_handler(CommandHandler("me", me))
    dp.add_handler(CommandHandler("set_name", set_name))
    dp.add_handler(CommandHandler("roll", roll))

    updater.start_polling()

    updater.idle()

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
