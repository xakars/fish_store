
def get_cart_template(cart_items):
    cart_template = ""
    for item in cart_items["data"]:
        cart_template += f"{item['name']}\n" \
                        f"{item['description']}\n" \
                        f"${item['unit_price']['amount']} per kg\n" \
                        f"{item['quantity']}kg in cart ${item['value']['amount']}\n\n" \

    cart_template += f"Total:${cart_items['meta']['display_price']['with_tax']['amount']}"
    return cart_template
