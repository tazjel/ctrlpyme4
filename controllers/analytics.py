# -*- coding: utf-8 -*-
#
# Author: Daniel J. Ramirez


import calendar
import datetime
import random
import json
from gluon.storage import Storage


hex_chars = [str(i) for i in range(0,9)] + ['A', 'B', 'C', 'D', 'E', 'F']


def time_interval_query(tablename, start_date, end_date):
    return (db[tablename].created_on >= start_date) & (db[tablename].created_on < end_date)


def analize(queries):
    pass


@auth.requires_membership("Analytics")
def cash_out():
    """ Returns the specified date, information

        args: [year, month, day]
        vars: [id_cash_out]
    """

    year, month, day = None, None, None
    try:
        year, month, day = int(request.args(0)), int(request.args(1)), int(request.args(2))
    except:
        today = datetime.date.today()
        year, month, day = today.year, today.month, today.day
    if not year or not month or not day:
        raise HTTP(400)
    cash_out = db.cash_out(request.vars.id_cash_out)
    if not cash_out:
        raise HTTP(404)
    seller = cash_out.id_seller

    date = datetime.date(year, month, day)
    start_date = datetime.datetime(date.year, date.month, date.day, 0)
    end_date = start_date + CASH_OUT_INTERVAL

    if not (cash_out.created_on > start_date and cash_out.created_on < end_date):
        raise HTTP(405)

    payment_opts = db(db.payment_opt.is_active == True).select()
    # will be used to create a payments chart
    payment_opt_data = {}
    for payment_opt in payment_opts:
        payment_opt_data[str(payment_opt.id)] = {
            "color": random_color_mix(PRIMARY_COLOR), "label": payment_opt.name, "value": 0
        }

    sales = db((db.sale.id == db.sale_log.id_sale)
                & (db.sale_log.sale_event == 'paid')
                & (db.sale.id_store == session.store)
                & (db.sale.created_by == seller.id)
                & time_interval_query('sale', start_date, end_date)
                ).select(db.sale.ALL, orderby=db.sale.id)
    payments_query = (db.payment.id < 0)

    total = 0
    total_cash = 0
    # set payments query and total sold quantity
    for sale in sales:
        payments_query |= db.payment.id_sale == sale.id
        total += sale.total
    payment_index = 0
    payments = db(payments_query).select(orderby=db.payment.id_sale)
    for sale in sales:
        sale.total_change = 0
        sale.payments = {}
        sale.payments_total = 0
        sale.change = 0
        for payment in payments[payment_index:]:
            if payment.id_sale != sale.id:
                break
            sale.payments_total += payment.amount
            if not sale.payments.has_key(str(payment.id_payment_opt.id)):
                sale.payments[str(payment.id_payment_opt.id)] = Storage(dict(amount=payment.amount, change_amount=payment.change_amount))
            else:
                _payment = sale.payments[str(payment.id_payment_opt.id)]
                _payment.amount += payment.amount
                _payment.change_amount += payment.change_amount
            if payment.id_payment_opt.allow_change:
                total_cash += payment.amount - payment.change_amount
            sale.total_change += payment.change_amount
            sale.change += payment.change_amount
        sale.change = DQ(sale.change, True)
        payment_index += 1
    total = DQ(total, True)
    total_cash = DQ(total_cash, True)

    return locals()



def day_report_data(year, month, day):
    year = datetime.date.today().year if not year else year
    month = datetime.date.today().month if not month else month
    day = datetime.date.today().day if not day else day

    date = datetime.date(year, month, day)


    start_date = datetime.datetime(date.year, date.month, date.day, 0)
    end_date = start_date + datetime.timedelta(hours=23, minutes=59, seconds=59)

    # income
    sales_total_sum = db.sale.total.sum()
    income = db((db.sale.id_store == session.store)
                & (db.sale.is_done == True)
                & (db.sale.created_on >= start_date)
                & (db.sale.created_on <= end_date)
                ).select(sales_total_sum).first()[sales_total_sum] or DQ(0)
    # expenses
    purchases_total_sum =db.purchase.total.sum()
    expenses = db((db.purchase.id_store == session.store)
                & (db.purchase.is_done >= True)
                & (db.purchase.created_on >= start_date)
                & (db.purchase.created_on <= end_date)
                ).select(purchases_total_sum).first()[purchases_total_sum] or DQ(0)

    sales_data = {
        'labels': [],
        'datasets': [{
            'data': []
        }]
    }

    for hour in range(24):
        sales_data['labels'].append('%d:00' % hour)
        start_hour = datetime.datetime(date.year, date.month, date.day, hour)
        end_hour = start_hour + datetime.timedelta(hours=1)
        hour_sales = db((db.sale.id_store == session.store)
                      & (db.sale.is_done == True)
                      & (db.sale.created_on >= start_hour)
                      & (db.sale.created_on < end_hour)
                     ).select(sales_total_sum).first()[sales_total_sum] or 0
        sales_data['datasets'][0]['data'].append(float(hour_sales))
    sales_data = json.dumps(sales_data)
    return locals()



@auth.requires_membership("Analytics")
def day_report():
    """ Returns the specified date, information

        args: [year, month, day]
    """

    return day_report_data(int(request.args(0)), int(request.args(1)), int(request.args(2)))

    year, month, day = None, None, None
    try:
        year, month, day = int(request.args(0)), int(request.args(1)), int(request.args(2))
    except:
        raise HTTP(400)
    if not year or not month or not day:
        raise HTTP(400)

    date = datetime.date(year, month, day)

    start_date = datetime.datetime(date.year, date.month, date.day, 0)
    end_date = start_date + datetime.timedelta(hours=23, minutes=59, seconds=59)

    # income
    sales_total_sum = db.sale.total.sum()
    income = db((db.sale.id_store == session.store)
                & (db.sale.created_on >= start_date)
                & (db.sale.created_on <= end_date)
                ).select(sales_total_sum).first()[sales_total_sum] or 0
    # expenses
    purchases_total_sum = db.purchase.total.sum()
    expenses = db((db.purchase.id_store == session.store)
                & (db.purchase.is_done >= True)
                & (db.purchase.created_on >= start_date)
                & (db.purchase.created_on <= end_date)
                ).select(purchases_total_sum).first()[purchases_total_sum] or 0
    return locals()


@auth.requires_membership("Analytics")
def daily_report():
    """ """

    today = datetime.date.today()
    redirect(URL('day_report', args=[today.year, today.month, today.day]))


#TODO check if the selected interval has already passed
def daily_interval(month, year):
    # Days Of The Month
    dotm = calendar.monthrange(year, month)[1]
    # the first day of the specified month and year
    end_date = datetime.date(year, month, 1)
    # a month previous to the specified month
    start_date = end_date - datetime.timedelta(days=dotm)
    start_date = datetime.date(start_date.year, start_date.month, 1)

    timestep = datetime.timedelta(days=1)

    return start_date, end_date, timestep


def monthly_analysis(query, tablename, field, month, year):
    """ """

    start_date, end_date, timestep = daily_interval(month, year)

    current_date = start_date
    data_set = []
    field_sum = db[tablename][field].sum()
    while current_date + timestep < end_date:
        partial_sum = db(query
                        & (db[tablename].created_on >= current_date)
                        & (db[tablename].created_on < current_date + timestep)
                        ).select(field_sum).first()[field_sum]
        data_set.append(partial_sum or DQ(0))
        current_date += timestep
    return data_set


def stocks_table(item):
    def stock_row(row, fields):
        tr = TR()
        # the stock is from purchase
        if row.id_purchase:
            tr.append(TD(A(T('Purchase'), _href=URL('purchase', 'get', args=row.id_purchase.id))))
        # stock is from inventory
        elif row.id_inventory:
            tr.append(TD(A(T('Inventory'), _href=URL('inventory', 'get', args=row.id_inventory.id))))
        # stock is from credit note
        elif row.id_credit_note:
            tr.append(TD(A(T('Credit note'), _href=URL('credit_note', 'get', args=row.id_credit_note.id))))
        elif row.id_stock_transfer:
            tr.append(TD(A(T('Stock transfer'), _href=URL('stock_transfer', 'ticket', args=row.id_stock_transfer.id))))

        tr.append(TD(DQ(row.purchase_qty, True)))
        tr.append(TD(row['created_on'].strftime('%d %b %Y, %H:%M')))

        #TODO  add link to employee analysis
        tr.append(TD(row.created_by.first_name + ' ' + row.created_by.last_name))

        return tr

    return super_table('stock_item', ['purchase_qty'], (db.stock_item.id_item == item.id) & (db.stock_item.id_store == session.store), row_function=stock_row, options_enabled=False, custom_headers=['concept', 'quantity', 'created on', 'created by'], paginate=False, orderby=~db.stock_item.created_on, search_enabled=False)


@auth.requires_membership("Analytics")
def item_analysis():
    """
        args: [id_item]
    """

    item = db.item(request.args(0))
    main_image = db(db.item_image.id_item == item.id).select().first()

    existence = item_stock(item, id_store=session.store)['quantity']

    stocks = stocks_table(item)

    sales = db(
        # (db.bundle_item.id_bundle == db.item.id)
        (db.bag_item.id_bag == db.bag.id)
        & (db.sale.id_bag == db.bag.id)
        & (db.sale.id_store == session.store)
        & (db.bag_item.id_item == item.id)
    ).select(db.sale.ALL, db.bag_item.ALL, orderby=~db.sale.created_on)
    stock_transfers = db(
        # (db.bundle_item.id_bundle == db.item.id)
        (db.bag_item.id_bag == db.bag.id)
        & (db.stock_transfer.id_bag == db.bag.id)
        & (db.stock_transfer.id_store_from == session.store)
        & (db.bag_item.id_item == item.id)
    ).select(db.stock_transfer.ALL, db.bag_item.ALL, orderby=~db.stock_transfer.created_on)

    return locals()


@auth.requires_membership("Analytics")
def index():
    start_date, end_date, timestep = daily_interval(11, 2015)

    query = (db.purchase.id_store == session.store) & (db.purchase.is_active == True)

    day_data = day_report_data(None, None, None)
    income = day_data['income']
    expenses = day_data['expenses']
    today_sales_data_script = SCRIPT('today_sales_data = %s;' % day_data['sales_data'])

    employees_query = ((db.auth_membership.group_id == db.auth_group.id)
                    & (db.auth_user.id == db.auth_membership.user_id)
                    & (db.auth_user.registration_key == '')
                    & (db.auth_membership.user_id == db.auth_user.id)
                    & (db.auth_group.role == 'Sales checkout'))
    employees_data = super_table('auth_user', ['email'], employees_query, show_id=True, selectable=False, options_function=lambda row: option_btn('', URL('cash_out', 'create', args=row.id), T('Cash out')))

    return locals()
