import textwrap


def get_cart_template(cart_items):
    cart_template = """"""
    for item in cart_items["data"]:
        cart_template += textwrap.dedent(f"""
            {item['name']}
            {item['description']}
            {item['unit_price']['amount']} per kg
            {item['quantity']}kg in cart ${item['value']['amount']}\n
        """)
    cart_template += f"Total:${cart_items['meta']['display_price']['with_tax']['amount']}"

    return cart_template
