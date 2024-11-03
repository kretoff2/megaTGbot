import bot
import datetime
import traceback
import threading
import config


def start_bot():
    try:
        bot.run_bot()
    except Exception as _ex:
        if str(_ex) == "('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))" or\
                str(_ex) == "HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=25)":
            print("connect aborted. I'm restarting")
        else:
            print("error")
            offset = datetime.timezone(datetime.timedelta(hours=3))
            now = datetime.datetime.now(offset)
            with open(f"logs/{now.date()}.txt", "a") as file:
                print(_ex)
                tb = traceback.format_exc()
                file.write(f"[{now.time()}]\t{str(_ex)}\n\n{tb}\n\n")
            bot.bot.send_message(config.ADMIN_ID, f"Произошла ошибка {_ex}")
    finally:
        start_bot()

bot_thread = threading.Thread(target=start_bot)
bot_thread.start()