
def total_order_price(shopping_bag):
    total_price = 0
    for item in shopping_bag:
        total_price += item.quantity * item.item_to_buy.price
    return total_price
