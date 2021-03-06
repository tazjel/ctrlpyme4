# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('Ctrl',SPAN('PyME')),XML('&trade;&nbsp;'),
                  _class="",_href=URL('default', 'index'),
                  _id="web2py-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Bet@net'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################


response.menu = []


memberships = {}
for group in auth.user_groups.values():
    memberships[group] = True


# configuration menu
config_menu_items = []
if memberships.get('Config'):
    config_menu_items += [
        (T('Settings'), False, URL('settings', 'update_main'), None)
        , (T('Stores'), False, URL('store', 'index'), None)
        , (T('Employees'), False, URL('user', 'index'), None)
        , (T('Addresses'), False, URL('address', 'index'), None)
        , (T('Payment Options'), False, URL('payment_opt', 'index'), None)
        , (T('Measure Units'), False, URL('measure_unit', 'index'), None)
        , (T('Taxes'), False, URL('tax', 'index'), None)
    ]
if memberships.get('Clients management'):
    config_menu_items += [
        (T('Clients'), False, URL('client', 'index'), None)
    ]
if memberships.get('Safe config') or memberships.get('Config'):
    config_menu_items += [
        (T('Paper sizes'), False, URL('paper_size', 'index'), None)
        , (T('Label pages'), False, URL('labels_page_layout', 'index'), None)
        , (T('Highlights'), False, URL('highlight', 'index'), None)
    ]

if config_menu_items:
    response.menu += [(T('Configuration'),False,None, config_menu_items)]

# items menu
if memberships.get("Items info"):
    if memberships.get("Items management"):
        submenu = [
              (T('Catalog'), False, URL('item', 'index'), None)
            , (T('Brands'), False, URL('brand', 'index'), None)
            , (T('Categories'), False, URL('category', 'index'), None)
            , (T('Traits'), False, URL('trait_category', 'index'), None)
            , (T('Transfers'), False, URL('stock_transfer', 'index'), None)
            , (T('Offers'), False, URL('offer_group', 'index'), None)
        ]
        if memberships.get('Product loss'):
            submenu.append(
                (T('Product losses'), False, URL('product_loss', 'index'), None)
            )
        response.menu += [
             (T('Items'), False, None, submenu)
        ]
    else:
        response.menu += [
             (T('Items'), False, URL('item', 'index'), [])
        ]


# purchases
if memberships.get('Purchases'):
    response.menu += [
        (T('Purchases'), False, None, [
             (T('List'), False, URL('purchase', 'index'), None)
            , (T('Suppliers'), False, URL('supplier', 'index'), None)
            , (T('Accounts payable'), False, URL('account_payable', 'index'), None)
        ])
    ]

# sales
if memberships.get('Sales invoices'):
    url = URL('sale', 'index')
    submenu = []
    if memberships.get('Sale orders'):
        url = None
        submenu += [(T('Orders'), False, URL('sale_order', 'index'), None)]
    if memberships.get('Sales returns'):
        url = None
        submenu += [(T('Credit notes'), False, URL('credit_note', 'index'), None)]
    if not url:
        submenu.insert(0, (T('List'), False, URL('sale', 'index'), None))
    submenu.append((T('Accounts receivable'), False, URL('account_receivable', 'index'), None))
    response.menu += [(T('Sales'), False, url, submenu)]

if memberships.get('Inventories'):
    response.menu += [(T('Inventory'), False, URL('inventory', 'index'), [ ])]


if memberships.get("Cash out"):
    response.menu += [ (T('Cash out'), False, URL('cash_out', 'index'), [ ]) ]


if memberships.get("Analytics"):
    response.menu += [
        (T('Analytics'), False, URL('analytics', 'index'), [ ])
    ]

if not memberships.get('Employee') and not memberships.get('Admin'):
    response.menu += [(T('Browse'), False, URL('item', 'browse'), [ ])]


response.auth_menu = []
if auth.is_logged_in():
    auth_menu = []

    if memberships.get('Admin') or memberships.get('Manager'):
        auth_menu += [
            (T('Change store'), False, URL('user', 'change_store'), [])
        ]
    auth_menu += [
            (T('Profile'), False, URL('user', 'profile'), [ ]),
            (T('Logout'), False, URL('default', 'user/logout'), [ ])
        ]

    response.auth_menu += [
        (auth.user.first_name, False, None, auth_menu)
    ]
else:
    response.auth_menu += [
        (T('guest'), False, None, [
            (T('Lost password'), False, URL('default', 'user/retrieve_password'), [ ]),
            (T('Login'), False, URL(
                'default', 'user/login',
                vars=dict(
                    __next=URL(request.controller, request.function,
                    args=request.args, vars=request.vars)
                )), [ ]
            )
        ])
    ]
