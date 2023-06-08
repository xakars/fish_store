import os
import logging
import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from store import (get_all_products,
                   get_token,
                   get_product_by_id,
                   get_product_price,
                   get_file_by_product_id,
                   get_file_by_id,
                   get_cart_by_reference,
                   add_product_to_cart,
                   get_cart_items_by_reference
                   )
from tools import save_image
from format_helper import get_cart_template


def start(update, context):
    products = get_all_products(access_token)["data"]
    keyboard = [
        [InlineKeyboardButton(f"{product['attributes']['name']}", callback_data=f"{product['id']}")] for product in products
    ]
    keyboard.append([InlineKeyboardButton("Корзина", callback_data='cart')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Please choose',
                             reply_markup=reply_markup)
    return "MENU"


def handle_menu(update, context):
    if update.callback_query.data == 'cart':
        chat_id = update.callback_query.message.chat_id
        cart_items = get_cart_items_by_reference(access_token, chat_id)
        text = get_cart_template(cart_items)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return

    product_id = update.callback_query.data
    product = get_product_by_id(access_token, product_id)

    product_attributes = product["data"]["attributes"]
    product_price = get_product_price(access_token, price_book_id, product_attributes["sku"])
    final_price = product_price["data"]["attributes"]["currencies"]["USD"]["amount"]

    template = f"{product_attributes['name']}\n\n" \
               f"${final_price} per kg\n" \
               f"100kg on stock\n\n" \
               f"{product_attributes['description']}"

    product_file_id = get_file_by_product_id(access_token, product_id)["id"]
    prodict_photo = get_file_by_id(access_token, product_file_id)
    photo_url = prodict_photo["link"]["href"]
    photo_name = prodict_photo["file_name"]
    if os.path.exists(f"./media/{photo_name}"):
        with open(f"./media/{photo_name}", "rb") as file:
            photo = file.read()
            message = context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=template)
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=user_reply.message.message_id)

    else:
        path_to_img = save_image(photo_url, photo_name)
        with open(path_to_img, "rb") as file:
            photo = file.read()
            message = context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=template)
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=user_reply.message.message_id)

    keyboard = [
        [InlineKeyboardButton("1 kg", callback_data=f'1 {product_id}'),
         InlineKeyboardButton("5 kg", callback_data=f'5 {product_id}'),
         InlineKeyboardButton("10 kg", callback_data=f'10 {product_id}')],
        [InlineKeyboardButton("Корзина", callback_data='cart')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=message.message_id,
                                     caption=template, parse_mode='Markdown', reply_markup=reply_markup)
    return "HANDLE_DESCRIPTION"


def handle_description(update, context):
    if update.callback_query.data == 'back':
        products = get_all_products(access_token)["data"]
        keyboard = [
            [InlineKeyboardButton(f"{product['attributes']['name']}", callback_data=f"{product['id']}")] for product in
            products
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Please choose',
                                 reply_markup=reply_markup)
        context.bot.delete_message(chat_id=update.effective_chat.id,
                                   message_id=update.callback_query.message.message_id)
        return "MENU"
    elif update.callback_query.data == 'cart':
        chat_id = update.callback_query.message.chat_id
        cart_items = get_cart_items_by_reference(access_token, chat_id)
        text = get_cart_template(cart_items)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    else:
        chat_id = update.callback_query.message.chat_id
        cart_id = get_cart_by_reference(access_token, chat_id)
        quantity, product_id = update.callback_query.data.split()
        add_product_to_cart(access_token, cart_id, product_id, quantity)
        print("Товар добавлен")
        return "HANDLE_DESCRIPTION"


def handle_users_reply(update, context):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = r.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(update, context)
        r.set(chat_id, next_state)
    except Exception as err:
        print(err)


if __name__ == '__main__':
    r = redis.Redis(host='localhost', port=6379, db=0)

    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    price_book_id = os.environ["PRICE_BOOK_ID"]

    access_token = get_token(client_id, client_secret)

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
