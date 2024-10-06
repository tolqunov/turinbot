from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN, ADMIN_ID, CHANNEL, messages, json
import re

def get_blocked_users():
    with open("blocked_users.json", "r") as file:
        return json.load(file)

def block_user(user_id):
    blocked_users = get_blocked_users()
    if user_id not in blocked_users:
        blocked_users.append(user_id)
        with open("blocked_users.json", "w") as file:
            json.dump(blocked_users, file)

def unblock_user(user_id):
    blocked_users = get_blocked_users()
    if user_id in blocked_users:
        blocked_users.remove(user_id)
        with open("blocked_users.json", "w") as file:
            json.dump(blocked_users, file)

def contains_url(message_text):
    url_regex = re.compile(
        r"(?:(?:http|https)://[^\s/$.?#].[^\s]*|[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}|@[\w_]+)"
    )
    return re.search(url_regex, message_text) is not None

bot = TeleBot(TOKEN)

def command_handler(message: Message):
    if message.text == "/start":
        bot.send_message(message.chat.id, messages['start'], parse_mode="HTML")
    elif message.text == "/help":
        bot.send_message(message.chat.id, messages['help'], parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "<b>Invalid Command</b> ❌", parse_mode="HTML")

def message_handler(message: Message):
    print(message.json)
    blocked_users = get_blocked_users()
    if str(message.chat.id) in blocked_users:
        approvement_keyboard = InlineKeyboardMarkup()
        approvement_keyboard.row(
            InlineKeyboardButton("✅ Approve", callback_data=f"approve {message.message_id} {message.chat.id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject {message.message_id} {message.chat.id}"),
            InlineKeyboardButton("🔓 Unblock User", callback_data=f"unblock {message.chat.id}")
        )
        bot.copy_message(ADMIN_ID, message.chat.id, message.message_id, reply_markup=approvement_keyboard)
        bot.send_message(message.chat.id, "<b>Your messages are being reviewed</b> 🔍", parse_mode="HTML")
    elif message.text:
        if contains_url(message.text):
            bot.send_message(message.chat.id, messages['url_review'], parse_mode="HTML")
            approvement_keyboard = InlineKeyboardMarkup()
            approvement_keyboard.row(
                InlineKeyboardButton("✅ Approve", callback_data=f"approve {message.message_id} {message.chat.id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject {message.message_id} {message.chat.id}"),
                InlineKeyboardButton("🛑 Block User", callback_data=f"block {message.chat.id}")
            )
            bot.copy_message(ADMIN_ID, message.chat.id, message.message_id, reply_markup=approvement_keyboard)
        else:
            mess = bot.copy_message(CHANNEL, message.chat.id, message.message_id)
            bot.send_message(message.chat.id, "<b>Message Sent</b> ✅", parse_mode="HTML")
            admin_buttons = InlineKeyboardMarkup()
            admin_buttons.row(
                InlineKeyboardButton("👌 Ignore", callback_data=f"ignore"),
                InlineKeyboardButton("🛑 Block User", callback_data=f"block {message.chat.id}"),
                InlineKeyboardButton("🗑 Delete Message", callback_data=f"delete {mess.message_id}")
            )
            admin_buttons.row(
                InlineKeyboardButton("🔗 Go to the post", url=f"t.me/{CHANNEL[1:]}/{mess.message_id}")
            )
            bot.copy_message(ADMIN_ID, message.chat.id, message.message_id, reply_markup=admin_buttons)
    
    elif message.photo or message.video or message.audio or message.voice or message.document:
        mess = bot.copy_message(CHANNEL, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "<b>Message Sent</b> ✅", parse_mode="HTML")
        admin_buttons = InlineKeyboardMarkup()
        admin_buttons.row(
            InlineKeyboardButton("👌 Ignore", callback_data=f"ignore"),
            InlineKeyboardButton("🛑 Block User", callback_data=f"block {message.chat.id}"),
            InlineKeyboardButton("🗑 Delete Message", callback_data=f"delete {mess.message_id}")
        )
        admin_buttons.row(
            InlineKeyboardButton("🔗 Go to the post", url=f"t.me/{CHANNEL[1:]}/{mess.message_id}")
        )
        bot.copy_message(ADMIN_ID, message.chat.id, message.message_id, reply_markup=admin_buttons)
    else:
        bot.send_message(message.chat.id, "<b>Invalid Message Content</b> ❌", parse_mode="HTML")

def inline_handler(call: CallbackQuery):
    data = call.data.split()
    if data[0] == "approve":
        bot.copy_message(CHANNEL, data[2], int(data[1]))
        bot.send_message(data[2], "<b>Message Sent</b> ✅", parse_mode="HTML")
        bot.answer_callback_query(call.id, "Message Approved")
        bot.delete_message(ADMIN_ID, call.message.message_id)
    elif data[0] == "reject":
        bot.answer_callback_query(call.id, "Message Rejected")
        bot.send_message(data[2], "<b>Message Rejected</b> ❌", parse_mode="HTML")
        bot.delete_message(ADMIN_ID, call.message.message_id)
    elif data[0] == "ignore":
        bot.answer_callback_query(call.id, "Ignored")
        bot.delete_message(ADMIN_ID, call.message.message_id)
    elif data[0] == "block":
        bot.answer_callback_query(call.id, "User Blocked")
        bot.send_message(ADMIN_ID, f"User {data[1]} blocked")
        block_user(data[1])
        bot.send_message(data[1], "<b>You have been blocked</b> 🚫", parse_mode="HTML")
    elif data[0] == "unblock":
        bot.answer_callback_query(call.id, "User Unblocked")
        bot.send_message(ADMIN_ID, f"User {data[1]} unblocked")
        unblock_user(data[1])
        bot.send_message(data[1], "<b>You have been unblocked</b> ✅", parse_mode="HTML")
    elif data[0] == "delete":
        bot.delete_message(CHANNEL, int(data[1]))
        bot.answer_callback_query(call.id, "Message Deleted")
        bot.delete_message(ADMIN_ID, call.message.message_id)