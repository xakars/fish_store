import requests
import datetime


access_token = None
timestamp = None
expires_in = None


def refresh_token(client_id, client_secret):
    url = "https://api.moltin.com/oauth/access_token"
    data = {"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"}
    response = requests.get(url, data=data)
    response.raise_for_status()
    dict_response = response.json()
    new_timestamp = dict_response["expires"]
    new_expires_in = dict_response["expires_in"]
    new_token = dict_response["access_token"]
    return new_timestamp, new_expires_in, new_token


def get_token(client_id, client_secret):
    global access_token, timestamp, expires_in
    if not access_token:
        timestamp, expires_in, access_token = refresh_token(client_id, client_secret)
        return access_token

    cr_time = datetime.datetime.now().timestamp()
    token_live_cycle = timestamp + expires_in
    if cr_time >= token_live_cycle:
        timestamp, expires_in, access_token = refresh_token(client_id, client_secret)
        return access_token
    else:
        return access_token


def get_all_products(token):
    url = "https://api.moltin.com/pcm/products"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def add_product_to_cart(token, reference, product_id, quantity):
    url = f"https://api.moltin.com/v2/carts/{reference}/items"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    data = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": int(quantity)
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def get_cart_by_reference(token, cart_id):
    url = f"https://api.moltin.com/v2/carts/{cart_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["data"]["id"]


def get_cart_items_by_reference(token, cart_id):
    url = f"https://api.moltin.com/v2/carts/{cart_id}/items"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def remove_cart_item(token, cart_id, product_id):
    url = f"https://api.moltin.com/v2/carts/{cart_id}/items/{product_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_product_by_id(token, product_id):
    url = f"https://api.moltin.com/pcm/products/{product_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    params = {'include': "component_products"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_product_price(token, price_books_id, product_sku):
    url = f"https://api.moltin.com/pcm/pricebooks/{price_books_id}"
    params = {"include": "prices"}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    items = response.json()["included"]
    price_id = ""
    for item in items:
        if product_sku in item["attributes"]["sku"]:
            price_id = item["id"]
    url = f"https://api.moltin.com/pcm/pricebooks/{price_books_id}/prices/{price_id}"
    response = requests.get(url, headers=headers)
    return response.json()


def get_file_by_product_id(token, product_id):
    url = f"https://api.moltin.com/pcm/products/{product_id}/relationships/main_image"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["data"]


def get_file_by_id(token, file_id):
    url = f"https://api.moltin.com/v2/files/{file_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["data"]


def create_customer(token, name, email):
    url = "https://api.moltin.com/v2/customers"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "data": {
            "type": "customer",
            "name": name,
            "email": email,
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
