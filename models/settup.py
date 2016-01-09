# Redirect the user to the store selection on controllers that requires it
if auth.is_logged_in():
    if not request.controller in ['address', 'appadmin', 'brand', 'category', 'default', 'item', 'item_image', 'measure_unit', 'payment_opt', 'search', 'store', 'tax', 'trait', 'trait_category', 'user', 'wallet']:

        # select the first store if theres only one
        if not session.store:
            stores = db(db.store.is_active == True).select()
            if len(stores) == 1:
                session.store = stores.first().id
        else:
            if not auth.has_membership('Store %s' % session.store) and not auth.has_membership('Admin'):
                redirect(URL('user', 'store_selection'))

        # redirect to store selection, when the user is a employee
        if not session.store and (request.controller != 'user' or request.function != 'store_selection') and auth.has_membership('Employee'):
            redirect(URL('user', 'store_selection'))
