import requests
from dotenv import load_dotenv
import os


def get_token(client_id, client_secret):
    url = "https://api.moltin.com/oauth/access_token"
    data = {"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"}
    response = requests.get(url, data=data)
    response.raise_for_status()
    bearer_token = response.json()["access_token"]
    return bearer_token


def get_all_products(token):
    url = "https://api.moltin.com/pcm/products"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def add_product_to_cart(token, reference, product_id):
    url = f"https://api.moltin.com/v2/carts/{reference}/items"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    data = {"data": {"id": product_id, "type": "cart_item", "quantity": 1}}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def create_custom_card(token):
    url = "https://api.moltin.com/v2/carts"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "data": {
            "name": "Petr’s cart",
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def get_cart_by_reference(token, cart_id):
    url = f"https://api.moltin.com/v2/carts/{cart_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


def get_cart_items_by_reference(token, cart_id):
    url = f"https://api.moltin.com/v2/carts/{cart_id}/items"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


def get_product_by_id(token, product_id):
    url = f"https://api.moltin.com/pcm/products/{product_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    params = {'include': "component_products"}
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def get_product_price(token, price_books_id, product_sku):
    url = f"https://api.moltin.com/pcm/pricebooks/{price_books_id}"
    params = {"include": "prices"}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers, params=params)
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
    return response.json()["data"]


def get_file_by_id(token, file_id):
    url = f"https://api.moltin.com/v2/files/{file_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()["data"]


if __name__ == "__main__":
    load_dotenv()
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    price_book_id = os.environ["PRICE_BOOK_ID"]
    access_token = get_token(client_id, client_secret)


    # print(create_custom_card(access_token))

    # get_cart_by_reference(access_token, "73d5abae-1a2a-4e29-be42-beac6414885d")
    #get_cart_items_by_reference(access_token, "73d5abae-1a2a-4e29-be42-beac6414885d")

    # products = get_all_products(access_token)
    # print(len(products["data"]))
    # products_id = [product["id"] for product in products["data"]]
    # print(products_id)
    # reference = "73d5abae-1a2a-4e29-be42-beac6414885d"
    # print(add_product_to_cart(access_token, reference, products_id[0]))

    #print(get_product_by_id(access_token, "1a6797f8-f561-4e56-a016-3380851f0845"))
    #print(get_price_product(access_token, price_book_id, "3"))

    #add_image_for_product(access_token, "1a6797f8-f561-4e56-a016-3380851f0845", "./images.jpeg")
    #print(get_file_by_product_id(access_token, "1a6797f8-f561-4e56-a016-3380851f0845"))
    print(get_file_by_id(access_token, "edbcb730-77a2-4fa4-aca7-21f2be2cb1ae"))

