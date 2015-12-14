# -*- coding: utf-8 -*-
#
# Author: Daniel J. Ramirez


# def client_order_row(row, fields):
#     tr = TR()
#     # sale status
#     last_log = db(db.sale_log.id_sale == row.id).select().last()
#     sale_event = last_log.sale_event if last_log else None
#     tr.append(TD(T(sale_event or 'Unknown')))
#     for field in fields:
#         tr.append(TD(row[field]))
#     return tr


def client_order_options(row):
    td = TD()

    # view ticket
    td.append(option_btn('', URL('bag', 'ticket', args=row.id_bag.id), action_name=T('View ticket')))
    return td


@auth.requires_membership('Clients')
def client_profile():
    orders = db(db.sale_order.id_client == auth.user.id).select()
    orders_data = None
    orders_data = super_table('sale_order', ['is_ready'], (db.sale_order.id_client == auth.user.id), options_function=client_order_options, show_id=True, selectable=False)
    return locals()


@auth.requires_membership('Admin')
def create():
    return common_create('auth_user')


@auth.requires_membership('Admin')
def get():
    pass


@auth.requires_membership('Admin')
def get_employee():
    """
        args: [id_user]
    """
    employee = db.auth_user(request.args(0))
    if not employee:
        raise HTTP(404)

    stores = db(db.store.is_active == True).select()
    groups = db(db.auth_group.id > 0).select()
    # memberships = db(db.auth_membership.user_id == employee.id).select()

    return locals()


@auth.requires_membership('Admin')
def remove_employee_membership():
    """
        args: [id_user, group_name]
    """

    employee = db.auth_user(request.args(0))
    group = db(db.auth_group.role == request.args(1).replace('_', ' ')).select().first()

    if not employee or not group:
        raise HTTP(404)

    db((db.auth_membership.group_id == group.id)
     & (db.auth_membership.user_id == employee.id)
    ).delete()
    # db.auth_membership.insert(user_id=employee.id, group_id=group.id)

    return locals()


@auth.requires_membership('Admin')
def add_employee_membership():
    """
        args: [id_user, group_name]
    """

    employee = db.auth_user(request.args(0))
    group = db(db.auth_group.role == request.args(1).replace('_', ' ')).select().first()

    if not employee or not group:
        raise HTTP(404)

    db.auth_membership.insert(user_id=employee.id, group_id=group.id)

    return locals()


@auth.requires_membership('Admin')
def update():
    return common_update('auth_user', request.args)


@auth.requires_membership('Admin')
def delete():
    return common_delete('auth_user', request.args)


@auth.requires_membership('Admin')
def index():
    """ List of employees """

    employee_group = db(db.auth_group.role == 'Employee').select().first()
    query = (db.auth_membership.user_id == db.auth_user.id) & (db.auth_membership.group_id == employee_group.id) & (db.auth_membership.user_id != auth.user.id)
    data = super_table('auth_user', ['email'], query, options_function=lambda row: TD(option_btn('pencil', URL('get_employee', args=row.id)))
    )
    return locals()


@auth.requires_login()
def post_login():
    # set the current bag, if theres is one
    if not session.current_bag or db.bag(session.current_bag).id_store != session.store:
        some_active_bag = db((db.bag.is_active == True)
                           & (db.bag.completed == False)
                           & (db.bag.created_by == auth.user.id)
                           & (db.bag.id_store == session.store)
                           ).select().first()
        if some_active_bag:
            session.current_bag = some_active_bag.id
    redirect(URL('default', 'index'))


def post_logout():
    session.store = None
    session.current_bag = None
    redirect(URL('default', 'index'))


@auth.requires_login()
def store_selection():
    """ """

    if session.store or not auth.has_membership('Employee'):
        redirect(URL('default', 'index'))

    form = SQLFORM.factory(
        Field('store', "reference store", label=T('Store'), requires=IS_IN_DB(db, 'store.id', '%(name)s'))
    )

    if form.process().accepted:
        session.store = form.vars.store
        redirect(URL('user', 'post_login'))
        response.flash = "You are in store %s" % db(form.vars.store).name
    elif form.errors:
        response.flash = 'form has errors'
    return dict(form=form)
