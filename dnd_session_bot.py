#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import re
import sqlite3
import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from enum import IntEnum, auto

class Stats(IntEnum):
    _str = auto()
    _dex = auto()
    _con = auto()
    _int = auto()
    _wis = auto()
    _cha = auto()

#TG_TOKEN = os.getenv or something

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

def help(update: Update, context: CallbackContext):
    """Send a help message when the command /help is issued"""
    update.message.reply_text(
        "Commands:\n"
        "  /join"
        "  /set_name NAME [SURNAME]\n"
        "  /set_stats STR DEX CON INT WIS CHA\n"
        "  /str, /dex, /con, /int, /wis, /cha\n"
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
        except ValueError as e:
            print("vse` kon4ilos' huevo", e)
        connection.commit()
        connection.close()
        return function

    return wrapper

#-------------------------------------------------------------------------------

# def get_stats(function):

#     def wrapper(update: Update, context: CallbackContext):


@connect_db
def join(update: Update, context: CallbackContext, cursor):
    '''join -- register character/bot user'''
    id_user = update.effective_user.id
    id_group = update.effective_chat.id
    id_message = update.effective_message.message_id

    instruction =\
        """INSERT INTO character(id_user, id_group) VALUES(?, ?)"""
    variables = (id_user, id_group)
    cursor.execute(instruction, variables)
    context.bot.send_message(
        chat_id = update.effective_user.id,
        text = u''
    )

#-------------------------------------------------------------------------------
@connect_db
def me(update: Update, context: CallbackContext, cursor):
    """me -- character info"""
    #print( "bot_data", context.user_data )
    #print("effective message", update.effective_message)
    print(context.job)
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
        SELECT first_name, second_name, str, dex, con, int, wis, cha FROM character
        WHERE id_user==? AND id_group==?;
        """
    variables = (id_user, id_group)
    cursor.execute(instruction, variables)
    character = cursor.fetchone()
    stats = character[-6:]
    character = character[:2]
    character = ' '.join([name for name in character if name])
    answer =\
        f"""\
        You've remembered that you are {character}
  Strength     : {stats[0]}
  Dexterity    : {stats[1]}
  Constitution : {stats[2]}
  Intelligence : {stats[3]}
  Wisdom       : {stats[4]}
  Charisma     : {stats[5]}
        """

    context.bot.send_message(
        chat_id = id_group,
        text = answer,
        reply_to_message_id=id_message
    )
    return False

#-------------------------------------------------------------------------------

@connect_db
def get_stat(update: Update, context: CallbackContext, cursor):
    stat = update.message.text[1:]
    print(stat)
    instruction =\
        f"""SELECT {stat} FROM character WHERE (id_user = ?) and (id_group = ?);"""
    variables = (update.effective_user.id, update.effective_chat.id)
    cursor.execute(instruction, variables)
    stat_value = (int(cursor.fetchone()[0]) - 10) // 2
    dice_roll = [random.randint(1,20)+ stat_value]
    answer = \
        f"""{stat} check : {dice_roll} (1d20) {stat_value:+}"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer,
        reply_to_message_id=update.effective_message.message_id
    )

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
        text = answer)

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
    regexp = re.compile('^(?P<dice>\\d+d\\d+)(?P<modifier>([\+-]\d+)*)?$')
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
@connect_db
def set_stats(update: Update, context: CallbackContext, cursor):
    id_user = update.effective_user.id
    id_group = update.effective_chat.id
    if len(context.args) != 6:
        text =\
            "/set_stats [str] [dex] [con] [int] [wis] [cha]\n"\
            "A character has 6 stats: str, dex, con, int, wis, cha\n"\
            "The order is important"
        context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = text)
        return
    instruction =\
        '''
        UPDATE  character SET str = ?, dex = ?, con = ?, int = ?, wis = ?, cha = ?
        WHERE (id_user == ?) and (id_group = ?);
        '''

    variables = ([*context.args, id_user, id_group])
    print(variables)
    cursor.execute(instruction, variables)
    answer = "You look a bit different."
    context.bot.send_message(
        chat_id = id_group,
        text = answer,
        reply_to_message_id = update.effective_message.message_id)

def main():
    """Start bot"""
    updater = Updater(TG_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("me", me))
    dp.add_handler(CommandHandler("set_name", set_name))
    dp.add_handler(CommandHandler("roll", roll))
    dp.add_handler(CommandHandler("set_stats", set_stats))
    dp.add_handler(CommandHandler("dex", get_stat))
    dp.add_handler(CommandHandler("str", get_stat))
    dp.add_handler(CommandHandler("int", get_stat))
    dp.add_handler(CommandHandler("con", get_stat))
    dp.add_handler(CommandHandler("wis", get_stat))
    dp.add_handler(CommandHandler("cha", get_stat))
    

    updater.start_polling()

    updater.idle()

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
