"""
Telegram bot to perform selected operations on Compal CH7465LG
using connect-box
"""
import os
import asyncio
import logging
import yaml
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import connectbox

CONFIG_DOCKER = "/config/config.yaml"
CONFIG_LOCAL =  "./config/config.yaml"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def load_config():
    """Read the YAML config"""
    global CONFIG_DOCKER, CONFIG_LOCAL
    cfg = None
    # try opening local config first [direct execution]
    # if not found, try the docker config path [docker execution]
    for p in [CONFIG_LOCAL, CONFIG_DOCKER]:
        fp = os.path.abspath(p)
        logger.debug(f"Attempting to read from {fp}")
        if os.path.isfile(fp):
            with open(fp, 'r') as ymlfile:
                cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
                logger.info(f"Loaded config from {fp}")
                return cfg
    return cfg


def help(update, context):
    """Send a message when the command /help is issued."""
    commands = context.bot_data.get("commands")
    update.message.reply_text(
        'Supported commands:\n'+
        '\n'.join((f"/{c}" for c in commands))
    )


def cb_status(update, context):
    """status"""
    host = context.bot_data.get("host")
    password = context.bot_data.get("password")
    status = asyncio.run(connectbox.get_cmstatus(host, password))
    reply_text = \
        "Status:\n"+\
        "----------\n"+\
        "\n".join((f"{str(k)}:{str(v)}\n" for k,v in status.items()))
    update.message.reply_text(reply_text)


def cb_devices(update, context):
    """connected devices"""
    host = context.bot_data.get("host")
    password = context.bot_data.get("password")
    devices = asyncio.run(connectbox.get_devices(host, password))
    reply_text = \
        "Connected Devices:\n"+\
        "----------\n"+\
        "\n".join((f"{str(d)}\n" for d in devices))
    update.message.reply_text(reply_text)


def cb_downstream(update, context):
    """downstream"""
    host = context.bot_data.get("host")
    password = context.bot_data.get("password")
    downstream = asyncio.run(connectbox.get_downstream(host, password))
    reply_text = \
        "Downstream:\n"+\
        "----------\n"+\
        "\n".join((f"{str(u)}\n" for u in downstream))
    update.message.reply_text(reply_text)


def cb_upstream(update, context):
    """upstream"""
    host = context.bot_data.get("host")
    password = context.bot_data.get("password")
    upstream = asyncio.run(connectbox.get_upstream(host, password))
    reply_text = \
        "Upstream:\n"+\
        "----------\n"+\
        "\n".join((f"{str(u)}\n" for u in upstream))
    update.message.reply_text(reply_text)


def cb_temperature(update, context):
    """temperature"""
    host = context.bot_data.get("host")
    password = context.bot_data.get("password")
    temperature = asyncio.run(connectbox.get_temperature(host, password))
    reply_text = \
        "Temperature:\n"+\
        "----------\n"+\
        str(temperature)
    update.message.reply_text(reply_text)

def cb_ipv6filter(update, context):
    """ipv6 filter"""
    host = context.bot_data.get("host")
    password = context.bot_data.get("password")
    if len(context.args)==1 and context.args[0].isnumeric():
        idd = int(context.args[0])
        new_state = asyncio.run(connectbox.toggle_ipv6filter(host, password, idd))
        update.message.reply_text(f"New enable/disable status for {idd} is {new_state}")
    else:
        filters = asyncio.run(connectbox.get_ipv6filters(host, password))
        reply_text = \
            "IPv6 filters:\n"+\
            "----------\n"+\
            "\n".join((f"{str(f)}\n" for f in filters))
        update.message.reply_text(reply_text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    #global host, password, commands
    # load config
    try:
        cfg = load_config()
        token = cfg.get('telegram').get('token')
        chat_id = cfg.get('telegram').get('chat_id')
        host = cfg.get('connect_box').get('host')
        password = cfg.get('connect_box').get('password')
    except:
        logger.error(f"No or incorrect config")
        return 1

    # asyncio event loop


    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)
    updater.bot.send_message(chat_id=chat_id, text="tgconnectbox started")
    uf = Filters.chat(chat_id)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.bot_data['commands'] = []
    dp.bot_data['host'] = host
    dp.bot_data['password'] = password

    # on different commands - answer in Telegram
    dp.bot_data['commands'].append("help")
    dp.add_handler(CommandHandler("help", help, filters=uf))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # connect box commands
    dp.bot_data['commands'].append("status - get status")
    dp.add_handler(CommandHandler('status', cb_status, filters=uf))
    dp.bot_data['commands'].append("devices - get the list of active devices")
    dp.add_handler(CommandHandler('devices', cb_devices, filters=uf))
    dp.bot_data['commands'].append("downstream - get downstream details")
    dp.add_handler(CommandHandler('downstream', cb_downstream, filters=uf))
    dp.bot_data['commands'].append("upstream - get upstream details")
    dp.add_handler(CommandHandler('upstream', cb_upstream, filters=uf))
    dp.bot_data['commands'].append("temperature - get temperature")
    dp.add_handler(CommandHandler('temperature', cb_temperature, filters=uf))
    dp.bot_data['commands'].append("ipv6f- show IPv6 filters")
    dp.bot_data['commands'].append("ipv6f i - toggle enable/disable of the i-th IPv6 filter")
    dp.add_handler(CommandHandler('ipv6f', cb_ipv6filter, filters=uf))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()