import os
from tools import save_image


def get_cart_template(cart_items):
    cart_template = ""
    for item in cart_items["data"]:
        cart_template += f"{item['name']}\n" \
                        f"{item['description']}\n" \
                        f"${item['unit_price']['amount']} per kg\n" \
                        f"{item['quantity']}kg in cart ${item['value']['amount']}\n\n" \

    cart_template += f"Total:${cart_items['meta']['display_price']['with_tax']['amount']}"
    return cart_template


def get_photo_path(prodict_photo):
    photo_url = prodict_photo["link"]["href"]
    photo_name = prodict_photo["file_name"]
    if os.path.exists(f"./media/{photo_name}"):
        return f"./media/{photo_name}"
    else:
        path_to_img = save_image(photo_url, photo_name)
        return path_to_img
