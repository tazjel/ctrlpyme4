# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Bet@net
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Author Daniel J. Ramirez <djrmuv@gmail.com>


import common_utils
import user_utils
import bag_utils


@auth.requires_membership('Employee')
def employee_profile():
    return dict()



def profile():
    if auth.has_membership('Clients'):
        redirect(URL('client', 'profile'))
    elif auth.has_membership('Employee'):
        redirect(URL('employee_profile'))



@auth.requires_membership('Admin config')
def create():
    """ Create employee """

    form = SQLFORM(db.auth_user)
    if form.process().accepted:
        employee_group = db(db.auth_group.role == 'Employee').select().first()
        if employee_group:
            db.auth_membership.insert(user_id=form.vars.id, group_id=employee_group.id)
        response.flash = T('Employee') + ' ' + T('created')
        redirect(URL('get_employee', args=form.vars.id))
    elif form.errors:
        response.flash = T('Errors in form')
    return dict(form=form)




def create_admin_user():
    """ Create an admin user if there is no admin user """

    if not URL.verify(request, hmac_key=CONF.take('hmac.key')):
        raise HTTP(403)


    admin_group = db(db.auth_group.role == 'Admin').select().first()

    if db(db.auth_membership.group_id == admin_group.id).select().first():
        session.info = T("There is already an admin user")
        redirect(URL('default', 'index'))


    form = SQLFORM(db.auth_user)
    if form.process().accepted:
        import settup

        settup.settup_admin_user(form.vars.id)

        response.flash = T('Admin') + ' ' + T('created')
        redirect(URL('default', 'user/login'))
    elif form.errors:
        response.flash = T('Errors in form')

    return dict(form=form)



@auth.requires_membership('Admin')
def get():
    pass


@auth.requires_membership('Admin config')
def rand_employee_password():
    """ sets a random password for the specified user (only employees)
        args [employee_id]
    """
    if auth.has_membership(None, request.args(0), 'Employee'):
        employee = db.auth_user(request.args(0))
        if not employee:
            raise HTTP(404)
        new_password = auth.random_password()
        session.info = T('password set, the new password should be in the employee email')
        content = '<html> %s: <h2>%s</h2></html>' % (T('Your new password is'), new_password)
        subject = '[%s]: %s' % (COMPANY_NAME, T('Your password has been changed'))
        r = db(db.auth_user.id == employee.id).validate_and_update(password=new_password)
        if r.errors:
            raise HTTP(500)
        r = mail.send(to=[employee.email], subject=subject, message=content)

        redirect(URL('user', 'get_employee', args=employee.id))


@auth.requires_membership('Admin config')
def get_employee():
    """
        args: [id_user]
    """
    employee = db.auth_user(request.args(0))
    if not employee:
        raise HTTP(404)
    if employee.id == auth.user.id:
        redirect(URL('default', 'index'))

    stores = db(db.store.is_active == True).select()

    permission_cards = WORKFLOW_DATA[COMPANY_WORKFLOW].cards()

    groups = db(
        user_utils.extra_roles_query(employee, COMPANY_WORKFLOW)
    ).iterselect()

    return locals()


@auth.requires_membership('Admin config')
def set_employee_max_discount():
    employee = db.auth_user(request.args(0))
    if not employee or employee.id == auth.user.id:
        raise HTTP(404)

    discount = 0
    try:
        discount = D(request.args(1))
        discount = min(max(0, discount), 100)
    except:
        raise HTTP(405, T("Invalid amount"))

    employee.max_discount = discount
    employee.update_record()

    return locals()



@auth.requires_membership('Admin config')
def remove_employee_membership():
    """
        args: [id_user, group_name]
    """

    employee = db.auth_user(request.args(0))
    group = db(
        db.auth_group.role == request.args(1).replace('_', ' ')
    ).select().first()

    if not employee or not group:
        raise HTTP(404)
    if employee.id == auth.user.id:
        redirect(URL('default', 'index'))

    if group.role in user_utils.static_roles_list(employee, COMPANY_WORKFLOW):
        raise HTTP(405)

    db((db.auth_membership.group_id == group.id)
     & (db.auth_membership.user_id == employee.id)
    ).delete()

    return locals()


@auth.requires_membership('Admin config')
def add_employee_membership():
    """
        args: [id_user, group_name]
    """

    employee = db.auth_user(request.args(0))
    group = db(
        db.auth_group.role == request.args(1).replace('_', ' ')
    ).select().first()

    if not employee or not group:
        raise HTTP(404)
    if employee.id == auth.user.id:
        redirect(URL('default', 'index'))

    if group.role in user_utils.static_roles_list(employee, COMPANY_WORKFLOW):
        raise HTTP(405)

    db.auth_membership.insert(user_id=employee.id, group_id=group.id)

    return locals()


@auth.requires_membership('Admin config')
def set_access_card():
    user = db.auth_user(request.args(0))
    if not user:
        raise HTTP(404)
    if not auth.has_membership(None, user.id, 'Employee'):
        raise HTTP(401)
    if user.id == auth.user.id:
        redirect(URL('default', 'index'))
    card_index = int(request.args(1))

    try:
        user_utils.set_access_card(user, card_index, COMPANY_WORKFLOW)
    except:
        raise HTTP(500)

    return dict()


@auth.requires_membership('Admin config')
def update():
    return common_update('auth_user', request.args)


@auth.requires_membership('Admin config')
def delete():
    user = db.auth_user(request.args(0))
    if not user:
        raise HTTP(404)
    if user.id == auth.user.id:
        raise HTTP(405)

    user.is_active = False
    user.registration_key = 'blocked'
    user.update_record()

    redirection()


@auth.requires_membership('Admin config')
def undelete():
    user = db.auth_user(request.args(0))
    if not user:
        raise HTTP(404)

    user.is_active = True
    user.registration_key = ''
    user.update_record()

    redirection()



@auth.requires_membership('Admin config')
def index():
    """ List of employees """

    import supert
    Supert = supert.Supert()

    title = T('employees')
    def employee_options(row):
        options = supert.OPTION_BTN(
            'edit', URL('get_employee', args=row.id), title=T('edit')
        )
        if row.registration_key == '':
            options += supert.OPTION_BTN(
                'visibility_off', URL('delete', args=row.id, vars=dict(_next=URL('user', 'index', vars=request.vars))),
                title=T('hide')
            )
        else:
            options += supert.OPTION_BTN(
                'visibility', URL('undelete', args=row.id, vars=dict(_next=URL('user', 'index', vars=request.vars))),
                title=T('show')
            )
        return options

    query = (
        (db.auth_membership.user_id == db.auth_user.id) &
        (db.auth_membership.group_id == db.auth_group.id) &
        (db.auth_group.role == 'Employee') &
        (db.auth_membership.user_id != auth.user.id)
    )
    if request.vars.show_hidden != 'yes':
        query &= db.auth_user.registration_key == ''

    data = Supert.SUPERT(
        query,
        [db.auth_user.ALL],
        select_args=dict(distinct=db.auth_user.id),
        fields=[ 'first_name', 'last_name', 'email' ],
        options_func=employee_options)
    return locals()


@auth.requires_login()
def post_login():
    if not auth.has_membership('Clients') or auth.user.is_client:
        common_utils.select_store(True)

    bag_utils.auto_bag_selection()
    if request.vars.__next:
        request.vars._next = request.vars.__next
        del request.vars.__next

    redirection()


def post_logout():
    session.store = None
    session.current_bag = None
    redirect(URL('default', 'index'))


@auth.requires(
    auth.has_membership('Admin') or
    auth.has_membership('Manager') 
)

def change_store():
    """ Change the store once logged in """

    session.store = None

    redirect(URL('store_selection'))



@auth.requires_login()
def store_selection():
    """ """

    if not auth.has_membership('Employee') or session.store:
        redirect(URL('default', 'index'))

    user_stores_query = (db.store.id < 0)
    if auth.has_membership('Admin'):
        user_stores_query = (db.store.is_active == True)
    else:
        user_stores_query = (db.store.is_active == True)
        user_store_groups = db((db.auth_membership.group_id == db.auth_group.id)
                             & (db.auth_group.role.contains('Store '))
                             & (db.auth_membership.user_id == auth.user.id)
                             ).select(db.auth_group.role)
        extra_query = (db.store.id < 0)
        for user_store_group in user_store_groups:
            store_id = int(user_store_group.role.split(' ')[1])
            extra_query |= (db.store.id == store_id)
        user_stores_query = (user_stores_query & (extra_query))

    stores = db(user_stores_query).select()
    if len(stores) == 1:
        session.store = stores.first().id
        bag_utils.auto_bag_selection()
        redirection()

    form = SQLFORM.factory(
        Field('store', "reference store", label=T('Store'), requires=IS_IN_DB(db(user_stores_query), 'store.id', '%(name)s'))
    )

    if form.process().accepted:
        session.store = form.vars.store
        response.flash = T("You are in store") + " %s" % db.store(form.vars.store).name

        bag_utils.auto_bag_selection()

        redirection()
    elif form.errors:
        response.flash = T('form has errors')
    return dict(form=form)
