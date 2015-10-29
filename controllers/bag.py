# -*- coding: utf-8 -*-
#
# Author: Daniel J. Ramirez

#
# A bag is a storage for items that will be sold.
#

from decimal import Decimal as D
from decimal import ROUND_FLOOR
from math import floor


def get_valid_bag(id_bag, completed=False):
    try:
        bag = db((db.bag.id == id_bag)
               & (db.bag.id_store == session.store)
               & (db.bag.created_by == auth.user.id)
               & (db.bag.completed == completed)
               ).select().first()
        return bag
    except:
        return None


def money_format(value):
    return '$ ' + str(value)



def refresh_bag_data(id_bag):
    bag = db.bag(id_bag)

    bag_items = db(db.bag_item.id_bag == bag.id).select()

    subtotal = D(0)
    taxes = D(0)
    total = D(0)
    quantity = D(0)
    for bag_item in bag_items:
        subtotal += bag_item.sale_price * bag_item.quantity
        taxes += bag_item.sale_taxes * bag_item.quantity
        total += (bag_item.sale_taxes + bag_item.sale_price) * bag_item.quantity
        quantity += bag_item.quantity
    subtotal = money_format(DQ(subtotal, True))
    taxes = money_format(DQ(taxes, True))
    total = money_format(DQ(total, True))
    quantity = DQ(quantity, True, True)
    return dict(subtotal=subtotal, taxes=taxes, total=total, quantity=quantity)


@auth.requires_membership('Sales bags')
def modify_bag_item():
    """
        modifies the bag_item quantity.

        args:
            bag_item_id
    """

    bag_item = db.bag_item(request.args(0))
    if not get_valid_bag(bag_item.id_bag):
        raise HTTP(403)
    if not bag_item:
        raise HTTP(404)
    bag_item.quantity = request.vars.quantity if request.vars.quantity else bag_item.quantity
    if not bag_item.id_item.allow_fractions:
        bag_item.quantity = remove_fractions(bag_item.quantity)
    bag_item.quantity = DQ(bag_item.quantity)

    qty = item_stock(db.item(bag_item.id_item), session.store)['quantity']
    if qty < bag_item.quantity:
        bag_item.quantity = qty

    bag_item.update_record()
    bag_data = refresh_bag_data(bag_item.id_bag.id)
    return dict(status='ok', bag_item=bag_item, **bag_data)


@auth.requires_membership('Sales bags')
def set_bag_item(bag_item):
    """ modifies bag item data, in order to display it properly, this method does not modify the database """
    item = db.item(bag_item.id_item)
    # bag_item.name = item.name
    bag_item.base_price = money_format(DQ(item.base_price, True)) if item.base_price else 0
    bag_item.price2 = money_format(DQ(item.price2, True)) if item.price2 else 0
    bag_item.price3 = money_format(DQ(item.price3, True)) if item.price3 else 0
    bag_item.sale_price = money_format(DQ(bag_item.sale_price or 0, True))

    bag_item.measure_unit = item.id_measure_unit.symbol

    bag_item.barcode = item_barcode(item)
    stocks = item_stock(item, session.store)
    bag_item.stock = stocks['quantity'] if stocks else 0

    return bag_item


@auth.requires_membership('Sales bags')
def select_bag():
    """ Set the specified bag as the current bag. The current bag will be available as session.current_bag

        args:
            bag_id

    """

    try:
        bag = get_valid_bag(request.args(0))
        if not bag:
            raise HTTP(404)
        session.current_bag = bag.id
        subtotal = 0
        taxes = 0
        total = 0
        quantity = 0
        bag_items = []
        for bag_item in db(db.bag_item.id_bag == bag.id).select():
            subtotal += bag_item.sale_price * bag_item.quantity
            taxes += bag_item.sale_taxes * bag_item.quantity
            total += (bag_item.sale_price + bag_item.sale_taxes) * bag_item.quantity
            quantity += bag_item.quantity
            bag_item_modified = set_bag_item(bag_item)
            bag_items.append(bag_item_modified)
        quantity = DQ(quantity, True, True)
        subtotal = money_format(DQ(subtotal, True))
        taxes = money_format(DQ(taxes, True))
        total = money_format(DQ(total, True))

        return dict(bag=bag, bag_items=bag_items, subtotal=subtotal, total=total, taxes=taxes, quantity=quantity)
    except:
        import traceback
        traceback.print_exc();


@auth.requires_membership('Sales bags')
def add_bag_item():
    """
        args:
            id_item
    """

    try:
        item = db.item(request.args(0))
        bag = get_valid_bag(session.current_bag)

        id_bag = bag.id if bag else None

        if not item or not id_bag:
            raise HTTP(404)

        bag_item = db((db.bag_item.id_item == item.id)
                    & (db.bag_item.id_bag == id_bag)
                    ).select().first()

        # bundle: chack if theres stock for every item in the bundle
        item_stock_qty = float('inf')
        # TODO implement item bundle sale
        if item.is_bundle:
            bundle_items = db(db.bundle_item.id_bundle == item.id).select()
            # check for stock
            for bundle_item in bundle_items:

                stock_qty = item_stock(bundle_item.id_item, session.store)['quantity']
                item_stock_qty = min(floor(stock_qty / bundle_item.quantity), item_stock_qty)

                if stock_qty < bundle_item.quantity:
                    return dict(status="out of stock")
        else:
            item_stock_qty = DQ(item_stock(item, session.store)['quantity'])
        print item_stock_qty


        # if theres no stock notify the user
        item_stock_qty = DQ(item_stock(item, session.store)['quantity'])
        if not bag_item:
            base_qty = 1 if item_stock_qty >= 1 else item_stock_qty % 1
            if base_qty <= 0:
                return dict(status="out of stock")
            id_bag_item = db.bag_item.insert(id_bag=id_bag, id_item=item.id, quantity=base_qty, sale_price=item.base_price, product_name=item.name,
                sale_taxes=item_taxes(item, item.base_price))
            bag_item = db.bag_item(id_bag_item)
        else:
            base_qty = item_stock_qty - bag_item.quantity if item_stock_qty - bag_item.quantity < 1 else 1
            if base_qty <= 0:
                return dict(status="out of stock")
            bag_item.quantity += base_qty
            bag_item.update_record()

        bag_item = set_bag_item(bag_item)
        bag_data = refresh_bag_data(id_bag)

        return dict(bag_item=bag_item, **bag_data)
    except:
        import traceback
        traceback.print_exc()

@auth.requires_membership('Sales bags')
def delete_bag_item():
    """
        args:
            id_bag_item
    """

    bag_item = db.bag_item(request.args(0))
    if not get_valid_bag(bag_item.id_bag):
        raise HTTP(401)
    db(db.bag_item.id == request.args(0)).delete()
    bag_data = refresh_bag_data(bag_item.id_bag.id)
    return dict(status="ok", **bag_data)


@auth.requires_membership('Sales bags')
def discard_bag():
    try:
        bag = get_valid_bag(session.current_bag)
        if not bag:
            raise HTTP(401)
        removed_bag = session.current_bag
        if not bag:
            raise HTTP(404)
        db(db.bag_item.id_bag == bag.id).delete()
        db(db.bag.id == bag.id).delete()

        other_bag = db((db.bag.is_active == True)
                     & (db.bag.created_by == auth.user.id)
                     & (db.bag.id_store == session.store)
                     & (db.bag.completed == False)
                     ).select().first()
        if other_bag:
            session.current_bag = other_bag.id

        return dict(other_bag=other_bag, removed=removed_bag)
    except:
        import traceback
        traceback.print_exc()


@auth.requires_membership('Sales bags')
def change_bag_item_sale_price():
    price_index = request.args(0)
    bag_item = db.bag_item(request.args(1))
    access_code = request.args(2)

    if not (price_index or bag_item or access_code):
        raise HTTP(400)
    if not get_valid_bag(bag_item.id_bag):
        raise HTTP(401)
    user = db((db.auth_user.access_code == access_code)).select().first()
    if user:
        if auth.has_membership(None, user.id, role='VIP seller'):
            # change the item bag item sale price in db
            sale_price = bag_item.sale_price
            if price_index == '1':
                sale_price = bag_item.id_item.base_price
            elif price_index == '2':
                sale_price = bag_item.id_item.price2
            elif price_index == '3':
                sale_price = bag_item.id_item.price3
            bag_item.sale_price = sale_price
            bag_item.sale_taxes = item_taxes(bag_item.id_item, bag_item.sale_price or 0)
            bag_item.update_record()
        else:
            raise HTTP(401)
    else:
        raise HTTP(401)

    bag_data = refresh_bag_data(bag_item.id_bag.id)

    return dict(status="ok", **bag_data)


@auth.requires_membership('Sales bags')
def complete():
    bag = get_valid_bag(session.current_bag)
    if not bag:
        raise HTTP(404)
    bag.completed = True
    bag.update_record()

    if auth.has_membership('Sales checkout'):
        redirect(URL('sale', 'create', args=bag.id))
    else:
        redirect(URL('ticket', args=bag.id))


@auth.requires_membership('Sales bags')
def ticket():
    """
        args:
            bag_id
    """

    bag = get_valid_bag(request.args(0), completed=True)

    if not bag:
        raise HTTP(404)

    # bag items
    bag_items = db(db.bag_item.id_bag == bag.id).select()

    return locals()


@auth.requires(auth.has_membership('Sales checkout')
            or auth.has_membership('Admin')
            or auth.has_membership('Manager')
            )
def get():
    """
        args: bag_id
    """

    bag = db((db.bag.completed == True) & (db.bag.id == request.args(0)) & (db.bag.id_store == session.store)).select().first()
    if not bag:
        raise HTTP(404)
    return dict(bag=bag)


@auth.requires_membership('Sales bags')
def create():
    """
    """

    try:
        bag = db.bag.insert(id_store=session.store, completed=False)
        session.current_bag = bag.id

        return dict(bag=bag)
    except:
        import traceback
        traceback.print_exc()
