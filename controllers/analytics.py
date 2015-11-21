# -*- coding: utf-8 -*-
#
# Author: Daniel J. Ramirez


import calendar
import datetime
import random


hex_chars = [str(i) for i in range(0,9)] + ['A', 'B', 'C', 'D', 'E', 'F']


def time_interval_query(tablename, start_date, end_date):
    return (db[tablename].created_on >= start_date) & (db[tablename].created_on < end_date)


def analize(queries):
    pass


@auth.requires_membership("Analytics")
def cash_out():
    """ Returns the specified date, information

        args: [year, month, day]
        vars: [id_seller]
    """

    year, month, day = None, None, None
    try:
        year, month, day = int(request.args(0)), int(request.args(1)), int(request.args(2))
    except:
        today = datetime.date.today()
        year, month, day = today.year, today.month, today.day
    if not year or not month or not day:
        raise HTTP(400)
    seller = db.auth_user(request.vars.id_seller)
    if not seller:
        raise HTTP(404)

    date = datetime.date(year, month, day)
    start_date = datetime.datetime(date.year, date.month, date.day, 0)
    end_date = start_date + datetime.timedelta(hours=23, minutes=59, seconds=59)

    sales_data = db((db.sale.id == db.sale_log.id_sale)
                    & (db.sale_log.sale_event == 'paid')
                    & (db.sale.id_store == session.store)
                    & (db.sale.created_by == seller.id)
                    & time_interval_query('sale', start_date, end_date)
                    ).select()

    payment_opts = db(db.payment_opt.is_active == True).select()

    # will be used to create a pay chart
    payment_opt_data = {}
    for payment_opt in payment_opts:
        rand_hex = "#"
        for i in range(0, 4):
            rand_hex += hex_chars[random.randint(0, len(hex_chars) - 1)]
        rand_hex += "FF"
        payment_opt_data[str(payment_opt.id)] = {
            "color": rand_hex, "label": payment_opt.name, "value": 0
        }

    return locals()


@auth.requires_membership("Analytics")
def day_report():
    """ Returns the specified date, information

        args: [year, month, day]
    """

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
                ).select(sales_total_sum).first()[sales_total_sum] or DQ(0)
    # expenses
    purchases_total_sum =db.purchase.total.sum()
    expenses = db((db.purchase.id_store == session.store)
                & (db.purchase.is_done >= True)
                & (db.purchase.created_on >= start_date)
                & (db.purchase.created_on <= end_date)
                ).select(purchases_total_sum).first()[purchases_total_sum] or DQ(0)


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


@auth.requires_membership("Analytics")
def index():
    start_date, end_date, timestep = daily_interval(11, 2015)


    query = (db.purchase.id_store == session.store) & (db.purchase.is_active == True)
    print monthly_analysis(query, 'purchase', 'total', 11, 2015)

    return locals()