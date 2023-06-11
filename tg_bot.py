import os
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
                   get_cart_items_by_reference,
                   remove_cart_item,
                   create_customer
                   )
from format_helper import get_cart_template
from photo_save_tools import get_photo_path
import textwrap


def get_menu():
    access_token = get_token(client_id, client_secret)

    products = get_all_products(access_token)["data"]
    keyboard = [
        [InlineKeyboardButton(f"{product['attributes']['name']}", callback_data=f"{product['id']}")] for product in
        products
    ]
    keyboard.append([InlineKeyboardButton("Корзина", callback_data='cart')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def start(update, context):
    keyboard = get_menu()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Please choose',
                             reply_markup=keyboard)
    return "MENU"


def handle_menu(update, context):
    access_token = get_token(client_id, client_secret)

    if update.callback_query.data == 'cart':
        chat_id = update.callback_query.message.chat_id
        text, keyboard = get_user_cart(chat_id)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=keyboard
        )
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id
        )
        return "HANDLE_CART"

    user_reply = update.callback_query
    product_id = update.callback_query.data
    product = get_product_by_id(access_token, product_id)

    product_attributes = product["data"]["attributes"]
    product_price = get_product_price(access_token, price_book_id, product_attributes["sku"])
    final_price = product_price["data"]["attributes"]["currencies"]["USD"]["amount"]

    template = f"""
        {product_attributes['name']}
        {final_price} per kg
        100kg on stock
        {product_attributes['description']}
    """

    product_file_id = get_file_by_product_id(access_token, product_id)["id"]
    prodict_photo = get_file_by_id(access_token, product_file_id)
    path_to_photo = get_photo_path(prodict_photo)
    with open(f"{path_to_photo}", "rb") as file:
        photo = file.read()

    keyboard = [
        [InlineKeyboardButton("1 kg", callback_data=f'1 {product_id}'),
         InlineKeyboardButton("5 kg", callback_data=f'5 {product_id}'),
         InlineKeyboardButton("10 kg", callback_data=f'10 {product_id}')],
        [InlineKeyboardButton("Корзина", callback_data='cart')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=textwrap.dedent(template))
    context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=message.message_id,
                                     caption=textwrap.dedent(template), parse_mode='Markdown', reply_markup=reply_markup)
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=user_reply.message.message_id)

    return "HANDLE_DESCRIPTION"


def get_user_cart(chat_id):
    access_token = get_token(client_id, client_secret)

    cart_items = get_cart_items_by_reference(access_token, chat_id)
    text = get_cart_template(cart_items)
    cart_items = get_cart_items_by_reference(access_token, chat_id)
    keyboard = [
        [InlineKeyboardButton(f"Убрать из корзины {item['name']}", callback_data=f"{item['id']}")] for item in cart_items["data"]
    ]
    keyboard.append([InlineKeyboardButton("В меню", callback_data='menu')])
    keyboard.append([InlineKeyboardButton("Оплатить", callback_data='buy')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


def handle_cart(update, context):
    access_token = get_token(client_id, client_secret)

    if update.callback_query.data == 'menu':
        keyboard = get_menu()
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Please choose',
                                 reply_markup=keyboard)
        context.bot.delete_message(chat_id=update.effective_chat.id,
                                   message_id=update.callback_query.message.message_id)
        return 'MENU'
    elif update.callback_query.data == 'buy':
        text = 'Пришлите, пожалуйста, ваш email:'
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text)
        return 'WAITING_EMAIL'
    else:
        chat_id = update.callback_query.message.chat_id
        product_id = update.callback_query.data
        remove_cart_item(access_token, chat_id, product_id)
        text, keyboard = get_user_cart(chat_id)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text,
                                 reply_markup=keyboard)
        context.bot.delete_message(chat_id=update.effective_chat.id,
                                   message_id=update.callback_query.message.message_id)
    return "HANDLE_CART"


def handle_description(update, context):
    access_token = get_token(client_id, client_secret)

    if update.callback_query.data == 'back':
        keyboard = get_menu()
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Please choose',
                                 reply_markup=keyboard)

        context.bot.delete_message(chat_id=update.effective_chat.id,
                                   message_id=update.callback_query.message.message_id)
        return "MENU"

    elif update.callback_query.data == 'cart':
        chat_id = update.callback_query.message.chat_id
        text, keyboard = get_user_cart(chat_id)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text,
                                 reply_markup=keyboard)
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.callback_query.message.message_id)

        return "HANDLE_CART"

    else:
        chat_id = update.callback_query.message.chat_id
        cart_id = get_cart_by_reference(access_token, chat_id)
        quantity, product_id = update.callback_query.data.split()
        add_product_to_cart(access_token, cart_id, product_id, quantity)
        update.callback_query.answer("Товар успешно добавлен в корзину!")
        return "HANDLE_DESCRIPTION"


def handle_buy(update, context):
    access_token = get_token(client_id, client_secret)

    user_reply = update.message.text
    user_name = update.effective_chat.first_name
    text = f"Вы прислали мне эту почту: {user_reply}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    create_customer(access_token, user_name, user_reply)
    text = f"Cпасибо за заказ, мы скоро свяжемся с вами"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    keyboard = get_menu()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Please choose',
                             reply_markup=keyboard)
    return "MENU"


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
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': handle_buy
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

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
