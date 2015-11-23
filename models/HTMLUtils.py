# -*- coding: utf-8 -*-
#
# Author: Daniel J. Ramirez


def stock_info(item):
    available = True
    stock = 0
    if auth.has_membership('Employee'):
        stock = item_stock(item, session.store)['quantity']
        stock = fix_item_quantity(item, stock)
        if stock <= 0:
            stock = SPAN(T('Out of stock'), _class="text-danger")
            available = False
        else:
            stock = str(stock) + " " + T('Available')
    else:
        stock = item_stock(item)['quantity']
        if stock <= 0:
            stock = SPAN(T('Out of stock'), _class="text-danger")
            available = False
        else:
            stock = SPAN(T('Available'), _class="text-success")

    return stock


def item_card(item):
    """ """

    available = "Not available"
    available_class = "text-danger"

    # stock, available = stock_info(item)

    stock_qty = 0
    if not session.store:
        stock_data = item_stock(item)
        stock_qty = stock_data['quantity']
    else:
        stock_data = item_stock(item, session.store)
        stock_qty = stock_data['quantity']
    if stock_qty > 0:
        available_class = "text-success"
        available = "Available"

    item_options = DIV()
    # if auth.has_membership('Items info') or auth.has_membership('Items management') or auth.has_membership('Items prices'):
    #     item_options.append(
    #         A(I(_class="fa fa-pencil"), _class="btn btn-primary", _href=URL('item', 'update', args=item.id))
    #     )
    # if auth.is_logged_in():
    #     item_options.append(
    #         BUTTON(T("Add to bag"), _class="btn btn-primary", _onclick="add_bag_item(%s);" % item.id)
    #     )

    return DIV(
        DIV(_class="panel-heading"),
        DIV(
            H4(A(item.name, _href=URL('item', 'get_by_name', args=item.name))),
            H4(A(item.id_brand.name, _href=URL('item', 'get_by_brand', args=item.id_brand.id))),

            P(item.description),
            P(T(available), _class=available_class),
            item_options,
            _class="panel-body"
        ),
        _class="panel panel-default item-card"
    )


# def


def filter_menu(filter_data):
    """ """

    tablename = filter_data['tablename']
    sort_options = SELECT(_class="form-control")
    for sort_option in filter_data['sortby']:
        sort_options.append(OPTION(db[tablename][sort_option].label, _value=sort_option))

    return DIV(
        DIV(
            H5(T("Order by")),
            sort_options,
            _class="panel-body"
        ),
        _class="panel panel-default"
    )


def option_btn(icon_name, action_url=None, action_name='', onclick=None):
    click_action = onclick if onclick else 'window.location.href = "%s"' % action_url
    button = BUTTON(I(_class='fa fa-%s' % icon_name), T(action_name), _type='button', _class='btn btn-default', _onclick=click_action)
    return button



def default_row_function(row, fields):
    """ Returns a row with the columns specified by fields, from the specified row """

    tr = TR()
    for field in fields:
        tr.append(TD(row[field]))

    return tr



def hide_button(row):
    """" Returns a button that calls the delete_row javascript function """

    return option_btn('eye-slash', onclick='delete_rows("/%s", "", "")' % (row.id))


def default_options_function(row):
    """ Returns a column with a generci edit option and genertic delete javascript option """

    td = TD()
    # edit option
    td.append(option_btn('pencil', URL('update', args=row.id)))
    td.append(option_btn('eye-slash', onclick='delete_rows("/%s", "", "")' % (row.id)))
    return td


def super_table(table, fields, rows, row_function=default_row_function,
                options_function=default_options_function, options_enabled=True,
                show_id=False, selectable=True, custom_headers=[],
                extra_options=None):
    """ Returns a data table with the specified rows, if a row function is supplied then rows will follow the format stablished by that function, meaning that the row function should return a TR element, the row function has access to the row object and the fields array, if an options function is specified, then, option buttons will be appended as a row column (You must set options_enabled to True). The options_function must return a TD element. Set show_id to True of you want the table to display the id for the specific row, Set selectable to True if you want a multiselect environment, the multiselect work via javascript, so you will have a list of selected row ids. If custom headers has items then, those items will be used as the table headers, id and select will not be affected. extra_options is a function that will return a list of elements based on the specified row, that will be appended to the default options or the specified options (even though its not necesary to use extra options in a custom options environment).

        This function will use the database table field labels as table headers.
    """

    if not rows:
        return None

    thead = TR()
    if selectable:
        thead.append(TH(INPUT(_type='checkbox', _id='master_checkbox')))
    if show_id:
        thead.append(TH('#'))
    if custom_headers:
        for header in custom_headers:
            thead.append(TH(T(header)))
    else:
        for field in fields:
            thead.append(TH(db[table][field].label))
    if options_enabled:
        thead.append(TH(T('Options')))
    thead = THEAD(thead)

    tbody = TBODY()
    for row in rows:
        tr = row_function(row, fields)
        if selectable:
            tr.insert(0, INPUT(_type='checkbox', _class='row_checkbox', _value=row.id))
        if show_id:
            tr.insert(1, TD(row.id))
        if options_enabled:
            options_td = options_function(row)
            if extra_options:
                for extra_option in extra_options(row):
                    options_td.append(extra_option)
            tr.append(options_td)

        tbody.append(tr)
    table = TABLE(thead, tbody, _class="table table-hover")

    return table



def sqlform_field(id, label, content):
    return DIV(
                LABEL(T(label), _class="control-label col-sm-3"),
                DIV(content, _class="col-sm-9", _id=id + '_contents' ),
                _id=id, _class="form-group"
            )



def data_row(row, fields=[], deletable=True, editable=True, extra_options=[], controller=None, _vars={}, selectable=True):
    """ """
    options_enabled = deletable or editable or extra_options

    if not controller:
        controller = request.controller

    # per row checkbox
    tr = TH()
    if selectable:
        tr.append(INPUT(_type='checkbox', _class='row_checkbox', _value=row.id))
    for field in fields:
        td = ''
        # if the field is a list, we iterate over its elements to concatenate the the row fields into a  single column
        if type(field) == type([]):
            for inner_field in field:
                td += row[inner_field] + ' '
        else:
            td = row[field]
        tr.append(TD(td))
    # Options
    if options_enabled:
        vars_string = URL(vars=_vars).split('?')[1] if _vars else ''
        options_td = TD()
        if editable:
            options_td.append(option_btn('pencil', URL(controller, 'update', args=row.id, vars=_vars)))
        if deletable:
            delete_action = 'delete_rows("/%s", "", "%s")' % (row.id, vars_string)
            options_td.append(option_btn('eye-slash', onclick=delete_action))
        # options must be related to the row, for that reason this function only allows same controller urls, and also it asumes that the first argument in the specified action is the row id.
        if extra_options:
            for option in extra_options:
                icon_name = option['icon_name'] if option.has_key('icon_name') else ''
                url_action = option['url_action'] if option.has_key('url_action') else None
                onclick = option['onclick'] if option.has_key('onclick') else None
                url_args=option['url_args'] if option.has_key('url_args') else []
                url_args.insert(0, row.id)
                url = URL(controller, url_action, args=url_args, vars=_vars)

                option_name = option['name'] if option.has_key('name') else ''

                options_td.append(option_btn(icon_name, url, option_name, onclick))
        tr.append(options_td)

        return tr


def data_headers(headers=[], options_enabled=True, selectable=True):
    # the master checkbox
    thead = TH()
    if selectable:
        thead.append(INPUT(_type='checkbox', _id='master_checkbox'))
    for header in headers:
        thead.append(TH(T(header)))
    if options_enabled:
        thead.append(TH(T('Options')))

    return thead


def data_table(head_cols, rows):
    pass


def data_table(headers=[], rows=[], fields=[], deletable=True,
               editable=True, extra_options=[], controller='', _vars={},
               selectable=True):
    """ Creates a data table with multiselect via checkboxes

        headers: the table headers
        rows: the set of rows obtained from db
        fields: the fields of the row that will be placed as table data, a field can be a string or a list, when the field is a list, all the list fields will be placed as a single column.
    """

    options_enabled = deletable or editable or extra_options

    # the master checkbox
    thead = data_headers(headers=headers, options_enabled=options_enabled, selectable=selectable)
    thead = THEAD(thead)
    tbody = TBODY()
    for row in rows:
        tr = data_row(row, fields=fields, deletable=deletable, editable=editable, extra_options=extra_options, controller=controller, _vars=_vars, selectable=selectable)
        tbody.append(tr)
    table = TABLE(thead, tbody, _class="table table-hover")
    table = DIV(table, _class="table-responsive") # responsiveness

    return table
