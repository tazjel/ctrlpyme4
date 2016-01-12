# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)

import os


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    ## For production add lazy_tables=True for a huge boost in performance
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'],)
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

db.define_table(
  'wallet'
  , Field('wallet_code', notnull=True, label=T('Wallet code'), writable=False, readable=False)
  , Field('balance', 'decimal(16,6)', default=0, label=T('Balance'), writable=False, readable=False)
)

auth.settings.extra_fields['auth_user'] = [
        Field('access_code', default="000000", label=T('Access code'), readable=False, writable=False)
      , Field('id_wallet', 'reference wallet', label=T('Wallet'), readable=False, writable=False)
      , Field('access_card_index', 'integer', readable=False, writable=False)
      , Field('is_client', 'boolean', default=False, readable=False, writable=False)
]

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.sender')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.login_next = URL('user', 'post_login')
auth.settings.logout_next = URL('user', 'post_logout')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)


# #TODO:60 move validators to a module
# validators
class IS_BARCODE_AVAILABLE(object):
    def __init__(self, db, barcode='', error_message=T('Barcode already used')):
        self.db = db;
        self.barcode = barcode
        self.error_message = error_message
        self.record_id = None
    def set_self_id(self, id):
        self.record_id = id
    def __call__(self, value):
        if not value:
            return (value, None)

        barcodes = None
        if self.record_id:
            barcodes = self.db((self.db.item.id != self.record_id)
                               & ((self.db.item.sku == self.barcode)
                                | (self.db.item.ean == self.barcode)
                                | (self.db.item.upc == self.barcode))
                             ).select()
            # print barcodes.first().id
        else:
            barcodes = self.db((self.db.item.sku == self.barcode)
                             | (self.db.item.ean == self.barcode)
                             | (self.db.item.upc == self.barcode)
                             ).select()

        if not barcodes:
            return (value, None)
        else:
            return (value, self.error_message)
    def formatter(self, value):
        return value


# class HAS_BARCODE(object):
#     def __init__(self, sku, ean, upc, error_message=T('Barcode already used')):
#         self.barcode1 = sku
#         self.barcode2 = ean
#         self.barcode3 = upc
#         self.error_message = error_message
#     def __call__(self, value, value2, value3):
#         if not (value or value2 or value3):
#             return ()
#         if not value:
#             return (value, None)
#         barcodes = self.db((self.db.item.sku == self.barcode)
#                     | (self.db.item.ean == self.barcode)
#                     | (self.db.item.upc == self.barcode)
#                      ).select()
#         if not barcodes:
#             return (value, None)
#         else:
#             return (value, self.error_message)
#     def formatter(self, value):
#         return value



""" database class object creation (initialization) """

db.define_table(
    "company_config"
    , Field('param_name', label=T("Name"), writable=False)
    , Field('param_value', label=T("Value"))
    , Field('param_type', label=T("Type"), readable=False, writable=False, default="string")
    # used to create computed fields
    , Field('param_expr', label=T("Expr"), readable=False, writable=False)
    , Field('is_public', type="boolean", label=T("Is public"))
)


db.define_table("brand",
    Field("name", "string", default=None, label=T('Name')),
    Field("logo", "upload", default=None, label=T('Logo')),
    auth.signature)

db.define_table("trait_category",
    Field("name", "string", default=None, label=T('Name')),
    auth.signature)

db.define_table("measure_unit",
    Field("name", "string", default=None, label=T('Name')),
    Field("symbol", "string", default=None, label=T('Symbol')),
    auth.signature)

db.define_table("tax",
    Field("name", "string", default=None, label=T('Name')),
    Field("percentage", "integer", default=None, label=T('Percentage')),
    Field("symbol", "string", default=None, label=T('Symbol')),
    auth.signature,
    format='%(name)s')


db.define_table(
    "company"
    , Field('name', 'string', default=None, label=T('Name'))
)


db.define_table("payment_opt",
    Field("name", "string", default=None, label=T('Name')),
    Field("allow_change", "boolean", default=None, label=T('Allow change')),
    Field("requires_account", "boolean", default=None, label=T('Requires account')),
    Field("credit_days", "integer", default=None, label=T('Credit days')),
    auth.signature)

db.define_table("address",
    Field("street", "string", default=None, label=T('Street')),
    Field("exterior", "string", default=None, label=T('Exterior number')),
    Field("interior", "string", default=None, label=T('Interior number')),
    Field("neighborhood", "string", default=None, label=T('Neighborhood')),
    Field("city", "string", default=None, label=T('City')),
    Field("municipality", "string", default=None, label=T('Municipality')),
    Field("state_province", "string", default=None, label=T('State or Province')),
    Field("country", "string", default=None, label=T('Country')),
    Field("reference", "string", default=None, label=T('Address Reference')),
    auth.signature,
    format='%(street)s %(exterior)s %(interior)s %(neighborhood)s'
    )


db.define_table("category",
    Field("name", "string", default=None, label=T('Name')),
    Field("description", "text", default=None, label=T('Description')),
    Field("url_name", "string", default=None, label=T('URL Name'), readable=False, writable=False),
    Field("icon", "upload", default=None, label=T('Icon')),
    Field("parent", "reference category", label=T('Parent category'), readable=False, writable=False),
    Field("trait_category1", "reference trait_category", label=T('Trait')+" 1"),
    Field("trait_category2", "reference trait_category", label=T('Trait')+" 2"),
    Field("trait_category3", "reference trait_category", label=T('Trait')+" 3"),
    auth.signature)
db.category.parent.requires=IS_EMPTY_OR(IS_IN_DB(db, 'category.id', ' %(name)s %(description)s %(url_name)s %(icon)s %(parent)s %(trait_category1)s %(trait_category2)s %(trait_category3)s'))
db.category.trait_category1.requires=IS_EMPTY_OR(IS_IN_DB( db, 'trait_category.id', ' %(name)s'))
db.category.trait_category2.requires=IS_EMPTY_OR(IS_IN_DB( db, 'trait_category.id', ' %(name)s'))
db.category.trait_category3.requires=IS_EMPTY_OR(IS_IN_DB( db, 'trait_category.id', ' %(name)s'))


db.define_table("trait",
    Field("id_trait_category", "reference trait_category", label=T('Trait category')),
    Field("trait_option", "string", default=None, label=T('Option')),
    auth.signature)

db.define_table("item",
    Field("id_brand", "reference brand", label=T('Brand')),
    Field("categories", "list:reference category", label=T('Categories')),
    Field("traits", "list:reference trait", label=T("Traits"), readable=False, writable=False),
    Field("name", "string", default=None, label=T('Name')),
    Field("description", "text", default=None, label=T('Description')),
    Field("upc", "string", length=12, default=None, label=T('UPC')),
    Field("ean", "string", length=13, default=None, label=T('EAN')),
    Field("sku", "string", length=20, default=None, label=T('SKU')),
    Field("is_bundle", "boolean", default=False, label=T('Is bundle'), readable=False, writable=False),
    Field("has_inventory", "boolean", default=True, label=T('Has inventory')),
    Field("base_price", "decimal(16,6)", default=None, label=T('Base price')),
    Field("price2", "decimal(16,6)", default=None, label=T('Price')+" 2"),
    Field("price3", "decimal(16,6)", default=None, label=T('Price')+" 3"),
    Field("id_measure_unit", "reference measure_unit", label=T('Measure unit')),
    Field("taxes", "list:reference tax", label=T('Taxes')),
    Field("url_name", "string", default=None, label=T('URL Name'), readable=False, writable=False),
    Field("extra_data1", "string", default=None, label=T('Extra Data')+" 1"),
    Field("extra_data2", "string", default=None, label=T('Extra Data')+" 2"),
    Field("extra_data3", "string", default=None, label=T('Extra Data')+" 3"),
    Field("allow_fractions", "boolean", default=None, label=T('Allow fractions')),
    Field("thumb", "upload", default=None, label=T('Thumbnail')),
    Field("reward_points", "integer", default=None, label=T('Reward Points')),
    Field("is_returnable", "boolean", default=True, label=T('Is returnable')),
    Field("has_serial_number", "boolean", default=False, label=T('Has serial number')),
    auth.signature)
db.item.id_brand.requires=IS_IN_DB(db(db.brand.is_active == True), 'brand.id', ' %(name)s %(logo)s')
db.item.id_measure_unit.requires=IS_IN_DB( db, 'measure_unit.id', ' %(name)s %(symbol)s')
# db.item.taxes.requires=IS_IN_DB( db, 'db.tax.id', ' %(name)s', multiple=True)

db.item.sku.requires=IS_BARCODE_AVAILABLE(db, request.vars.sku)
db.item.ean.requires=IS_BARCODE_AVAILABLE(db, request.vars.ean)
db.item.upc.requires=IS_BARCODE_AVAILABLE(db, request.vars.upc)



db.define_table(
  'bundle_item'
  , Field('id_bundle', 'reference item')
  , Field('id_item', 'reference item')
  , Field('quantity', 'decimal(16,6)')
  , auth.signature
)


db.define_table("store",
    Field("id_address", "reference address", label=T('Address')),
    Field("name", "string", default=None, label=T('Name')),
    Field("consecutive", "integer", default=1, readable=False, writable=False),
    #Fields required for CFDI Invoice
    Field('certificate',type='upload',autodelete=True,readable=False,writable=False,
		uploadfolder=request.folder+'/private/',label=T("Certificate")+"(.cer)"),
	Field('private_key',type='upload',autodelete=True,readable=False,writable=False,
		uploadfolder=request.folder+'/private/',label=T("Private Key")+"(.key)"),
	Field('invoice_series', label=T("CFDI Series"),readable=False),
	#Completamente ocultos se generan cuando actualizas certificado
	Field('certificate_number',readable=False,writable=False),
	Field('certificate_base64',type="text",readable=False,writable=False),
	Field('certpem_base64',type="text",readable=False,writable=False),
    auth.signature)
# db.store.id_company.requires=IS_IN_DB( db, 'company.id', '')
db.store.id_address.requires=IS_IN_DB( db, 'address.id', ' %(street)s %(exterior)s %(interior)s %(neighborhood)s %(city)s %(municipality)s %(state_province)s %(country)s %(reference)s')



db.define_table(
    'store_role'
    , Field('id_user', "reference auth_user", label=T('user'))
    , Field('id_store', "reference store", label=T('store'))
    , Field('id_role', "reference auth_group", label=T('role'))
)

db.define_table("store_config",
    Field("id_store", "reference store", label=T('Store'), writable=False),
    Field("param_name", "string", default=None, label=T('Parameter name'), writable=False),
    Field("param_value", "string", default=None, label=T('Parameter value')),
    Field("param_type", "string", default=None, label=T('Parameter type'), writable=False),
    Field("is_public", "boolean", default=False, label=T('Is Public')),
    auth.signature)
db.store_config.id_store.requires=IS_IN_DB( db, 'store.id', ' %(id_address)s %(name)s')


db.define_table("supplier",
    Field("business_name", "string", default=None, label=T('Business Name')),
    Field("tax_id", "string", default=None, label=T('Tax ID')),
    Field("id_address", "reference address", label=T('Address')),
    auth.signature)

db.define_table("purchase",
    Field("id_payment_opt", "reference payment_opt", label=T('Payment option')),
    Field("id_supplier", "reference supplier", label=T('Supplier')),
    Field("id_store", "reference store", label=T('Store')),
    Field("invoice_number", "integer", default=None, label=T('Invoice number')),
    Field("subtotal", "decimal(16,6)", default=0, label=T('Subtotal')),
    Field("total", "decimal(16,6)", default=0, label=T('Total')),
    Field("shipping_cost", "decimal(16,6)", default=0, label=T('Shipping cost')),
    Field("tracking_number", "integer", default=None, label=T('Tracking number')),
    Field("is_done", "boolean", default=False, label=T('Done'), readable=False, writable=False),
    Field("purchase_xml", "text", default=None, label=T('XML'), readable=False, writable=False),
    auth.signature)
db.purchase.id_store.requires = IS_IN_DB(db(db.store.is_active == True), 'store.id', '%(name)s')


db.define_table("bag",
    Field("id_store", "reference store", label=T('Store'))
    , Field("subtotal", "decimal(16,6)", default=0, label=T('Subtotal'))
    , Field("taxes", "decimal(16,6)", default=0, label=T('Taxes'))
    , Field("total", "decimal(16,6)", default=0, label=T('Total'))
    , Field("completed", "boolean", default=False, label=T('Completed'))
    # this state is used to specify that the bag is being processed by the system
    , Field("is_on_hold", "boolean", default=False, label=T('On hold'))
    , auth.signature)


db.define_table("bag_item",
    Field("id_item", "reference item", label=T('Item')),
    Field("id_bag", "reference bag", label=T('Bag')),
    Field("quantity", "decimal(16,6)", default=1, label=T('Quantity')),
    Field("total_buy_price", "decimal(16,6)", default=None, label=T('Buy price')),
    Field("wavg_days_in_shelf", "integer", default=None, label=T('Average shelf life')),
    Field("sale_price", "decimal(16,6)", default=None, label=T('Sale price')),
    Field("sale_taxes", "decimal(16,6)", default=None, label=T('Sale taxes')),
    Field("product_name", "string", default=None, label=T('Product name')),
    Field("sale_code", "string", default=None, label=T('Sale code')),
    Field("serial_number", "string", default=None, label=T('Serial number')),
    auth.signature)

db.define_table("sale",
    Field("id_bag", "reference bag", label=T('Bag'), readable=False, writable=False),
    Field("consecutive", "integer", default=None, label=T('Consecutive'), readable=False, writable=False),
    Field("subtotal", "decimal(16,6)", default=None, label=T('Subtotal'), readable=False, writable=False),
    Field("taxes", "decimal(16,6)", default=None, label=T('Taxes'), readable=False, writable=False),
    Field("total", "decimal(16,6)", default=None, label=T('Total'), readable=False, writable=False),
    Field("quantity", "decimal(16,6)", default=None, label=T('Quantity'), readable=False, writable=False),
    Field("reward_points", "integer", default=None, label=T('Reward Points'), readable=False, writable=False),
    Field("id_client", "reference auth_user", default=None, label=T('Client')),
    Field("is_invoiced", "boolean", default=None, label=T('Is invoiced'), readable=False, writable=False),
    Field("id_store", "reference store", label=T('Store'), writable=False, readable=False),
    auth.signature)
db.sale.id_client.requires = IS_EMPTY_OR(IS_IN_DB(db((db.auth_user.is_client == True) & (db.auth_user.registration_key == "")), 'auth_user.id', '%(email)s'))


db.define_table("sale_log",
    Field("id_sale", "reference sale", label=T('Sale')),
    Field("sale_event", "string", default=None, label=T('Event')),
    Field("event_date", "datetime", default=None, label=T('Date')),
    auth.signature)

db.define_table("credit_note",
    Field("id_sale", "reference sale", label=T('Sale')),
    Field("subtotal", "decimal(16,6)", default=None, label=T('Subtotal')),
    Field("total", "decimal(16,6)", default=None, label=T('Total')),
    Field("is_usable", "boolean", default=None, label=T('Is usable')),
    Field("code", "string", default=None, label=T('Code')),
    auth.signature)

db.define_table("credit_note_item",
    Field("id_credit_note", "reference credit_note", label=T('Credit note')),
    Field("id_bag_item", "reference bag_item", label=T('Bag Item')),
    Field("quantity", "decimal(16,6)", default=None, label=T('Quantity')))


db.define_table(
  'sale_order'
  , Field('id_client', 'reference auth_user', label=T('Client'), readable=False, writable=False)
  , Field('id_bag', 'reference bag', label=T('Bag'), readable=False, writable=False)
  , Field('id_sale', 'reference sale', default=None, label=T('Sale'), readable=False, writable=False)
  , Field('id_store', 'reference store', label=T('Store'))
  , Field('is_ready', 'boolean', default=False, label=T('Ready'), readable=False, writable=False)
  , auth.signature
)
db.sale_order.id_store.requires = IS_IN_DB(db, 'store.id')


db.define_table("inventory",
    Field("id_store", "reference store", label=T('Store')),
    Field("is_partial", "boolean", default=None, label=T('Is partial')),
    Field("is_done", "boolean", default=None, label=T('Is done')),
    auth.signature)

db.define_table("inventory_item",
    Field("id_inventory", "reference inventory", label=T('Inventory')),
    Field("id_item", "reference item", label=T('Item')),
    Field("system_qty", "integer", default=None, label=T('System quantity')),
    Field("physical_qty", "integer", default=None, label=T('Physical quantity')),
    Field("is_missing", "boolean", default=False, label=T('Is missing'))
    )


db.define_table("stock_item",
    Field("id_purchase", "reference purchase", label=T('Purchase')),
    # When the item is returned we have to create a stock item with the
    # associated credit note
    Field("id_credit_note", "reference credit_note", label=T('Credit note')),
    # When there are more items than those registered by the system, we have to add stock related to that inventory
    Field("id_inventory", "reference inventory", label=T('Inventory')),
    # to simplify queries
    Field("id_store", "reference store", label=T('Store')),
    Field("id_item", "reference item", label=T('Item')),
    Field("purchase_qty", "decimal(16,6)", default=None, label=T('Purchase quantity')),
    Field("stock_qty", "decimal(16,6)", default=0, label=T('Stock quantity')),
    # the buy price
    Field("price", "decimal(16,6)", default=None, label=T('Price')),
    Field("taxes", "decimal(16,6)", default=None, label=T('Taxes')),
    Field("serial_numbers", "text", default=None, label=T('Serial numbers')),
    # base sale price, this will update the item base price when the purchase is applied
    Field("base_price", "decimal(16,6)", default=0, label=T('Base price')),
    Field("price2", "decimal(16,6)", default=0, label=T('Price') + '2'),
    Field("price3", "decimal(16,6)", default=0, label=T('Price') + '3'),
    auth.signature)


db.define_table("payment",
    Field("id_payment_opt", "reference payment_opt", label=T('Payment option')),
    Field("id_sale", "reference sale", label=T('Sale')),
    # used to reference the payment before the sale creation
    Field("id_bag", "reference bag", label=T('bag')),
    Field("amount", "decimal(16,6)", default=0, label=T('Amount')),
    Field("account", "string", default=None, label=T('Account')),
    Field("change_amount", "decimal(16,6)", default=0, label=T('Change amount')),
    Field("wallet_code", default=None, label=T('Wallet code')),
    auth.signature)


db.define_table("item_image",
    Field("id_item", "reference item", label=T('Item'), readable=False, writable=False),
    Field("image", "upload", default=None, label=T('Image'), uploadfolder=os.path.join(request.folder, 'static/uploads')),
    Field("thumb", "upload", default=None, label=T('Thumbnail'), readable=False, writable=False, uploadfolder=os.path.join(request.folder, 'static/uploads')),
    Field("sm", "upload", default=None, label=T('Small'), readable=False, writable=False, uploadfolder=os.path.join(request.folder, 'static/uploads')),
    Field("md", "upload", default=None, label=T('Medium'), readable=False, writable=False, uploadfolder=os.path.join(request.folder, 'static/uploads')),
    Field("lg", "upload", default=None, label=T('Large'), readable=False, writable=False, uploadfolder=os.path.join(request.folder, 'static/uploads')),
)
db.item_image.image.requires = IS_IMAGE(extensions=('jpeg', 'png'))
# db.item_image.thumb.requires = IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg', 'png')))
# db.item_image.small.requires = IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg', 'png')))
# db.item_image.medium.requires = IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg', 'png')))
# db.item_image.large.requires = IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg', 'png')))


db.define_table("promotion",
    Field("id_store", "reference store", label=T('Store')),
    Field("json_data", "text", default=None, label=T('JSON data')),
    Field("code", "string", default=None, label=T('Code')),
    Field("starts_on", "datetime", default=None, label=T('Starts on')),
    Field("ends_on", "datetime", default=None, label=T('Ends on')),
    Field("is_coupon", "boolean", default=None, label=T('Is coupon')),
    Field("is_combinable", "boolean", default=None, label=T('Is combinable')),
    auth.signature)

db.define_table("account_receivable",
    Field("id_sale", "reference sale", label=T('Sale')),
    Field("is_settled", "boolean", default=None, label=T('Is settled')),
    auth.signature)

db.define_table("account_payable",
    Field("id_purchase", "reference purchase", label=T('Purchase')),
    Field("is_settled", "boolean", default=None, label=T('Is settled')),
    auth.signature)

db.define_table("tax_data",
    Field("tax_id", "integer", default=None, label=T('Tax ID')),
    Field("business_name", "string", default=None, label=T('Business Name')),
    Field("id_address", "reference address", label=T('Address')),
    auth.signature)

db.define_table("invoice",
    Field("id_sale", "reference sale", label=T('Sale')),
    Field("id_tax_data", "reference tax_data", label=T('Tax data')),
    Field("invoice_xml", "text", default=None, label=T('XML')),
    Field("uuid", "string", default=None, label=T('UUID')),
    Field("sat_seal", "string", default=None, label=T('SAT Seal')),
    Field("certification_date", "datetime", default=None, label=T('Certification date')),
    Field("folio", "integer", default=None, label=T('Folio')),
    Field("is_cancelled", "boolean", default=None, label=T('Is cancelled')),
    Field("cancel_date", "datetime", default=None, label=T('Cancel date')),
    Field("acknowledgement", "text", default=None, label=T('Acknowledgement')),
    auth.signature)

""" Relations between tables (remove fields you don't need from requires) """


db.trait.id_trait_category.requires=IS_IN_DB( db, 'trait_category.id', ' %(name)s')
db.purchase.id_payment_opt.requires=IS_IN_DB( db, 'payment_opt.id', ' %(name)s %(allow_change)s %(credit_days)s')
db.purchase.id_supplier.requires=IS_IN_DB( db, 'supplier.id', ' %(business_name)s %(tax_id)s %(id_address)s')
# db.purchase.id_store.requires=IS_IN_DB( db, 'store.id', ' %(id_company)s %(id_address)s %(name)s')
db.supplier.id_address.requires=IS_IN_DB( db, 'address.id', ' %(street)s %(exterior)s %(interior)s %(neighborhood)s %(city)s %(municipality)s %(state_province)s %(country)s %(reference)s')

# db.bag.id_store.requires=IS_IN_DB( db, 'store.id', ' %(id_company)s %(id_address)s %(name)s')
db.bag_item.id_bag.requires=IS_IN_DB( db, 'bag.id', ' %(id_store)s %(completed)s')
db.sale.id_bag.requires=IS_IN_DB( db, 'bag.id', ' %(id_store)s %(completed)s')
# db.sale.id_store.requires=IS_IN_DB( db, 'store.id', ' %(id_company)s %(id_address)s %(name)s')
db.sale_log.id_sale.requires=IS_IN_DB( db, 'sale.id', ' %(id_bag)s %(number)s %(subtotal)s %(total)s %(quantity)s %(client)s %(reward_points)s %(is_invoiced)s %(id_store)s')
db.credit_note.id_sale.requires=IS_IN_DB( db, 'sale.id', ' %(id_bag)s %(number)s %(subtotal)s %(total)s %(quantity)s %(client)s %(reward_points)s %(is_invoiced)s %(id_store)s')
db.credit_note_item.id_credit_note.requires=IS_IN_DB( db, 'credit_note.id', ' %(id_sale)s %(subtotal)s %(total)s %(is_usable)s %(code)s')
db.credit_note_item.id_bag_item.requires=IS_IN_DB( db, 'bag_item.id', ' %(id_item)s %(id_bag)s %(quantity)s %(buy_price)s %(buy_date)s %(sale_price)s %(sale_taxes)s %(product_name)s %(sale_code)s %(serial_number)s')
# db.inventory.id_store.requires=IS_IN_DB( db, 'store.id', ' %(id_company)s %(id_address)s %(name)s')
db.inventory_item.id_inventory.requires=IS_IN_DB( db, 'inventory.id', ' %(id_store)s %(is_partital)s %(done)s')
db.payment.id_payment_opt.requires=IS_IN_DB( db, 'payment_opt.id', ' %(name)s %(allow_change)s %(credit_days)s')
db.payment.id_sale.requires=IS_IN_DB( db, 'sale.id', ' %(id_bag)s %(number)s %(subtotal)s %(total)s %(quantity)s %(client)s %(reward_points)s %(is_invoiced)s %(id_store)s')
# db.promotion.id_store.requires=IS_IN_DB( db, 'store.id', ' %(id_company)s %(id_address)s %(name)s')
db.account_receivable.id_sale.requires=IS_IN_DB( db, 'sale.id', ' %(id_bag)s %(number)s %(subtotal)s %(total)s %(quantity)s %(client)s %(reward_points)s %(is_invoiced)s %(id_store)s')
db.account_payable.id_purchase.requires=IS_IN_DB( db, 'purchase.id', ' %(id_payment_opt)s %(id_supplier)s %(id_store)s %(invoice_number)s %(subtotal)s %(total)s %(shipping_cost)s %(tracking_number)s')
db.invoice.id_sale.requires=IS_IN_DB( db, 'sale.id', ' %(id_bag)s %(number)s %(subtotal)s %(total)s %(quantity)s %(client)s %(reward_points)s %(is_invoiced)s %(id_store)s')
db.invoice.id_tax_data.requires=IS_IN_DB( db, 'tax_data.id', ' %(tax_id)s %(business_name)s %(id_address)s')
db.tax_data.id_address.requires=IS_IN_DB( db, 'address.id', ' %(street)s %(exterior)s %(interior)s %(neighborhood)s %(city)s %(municipality)s %(state_province)s %(country)s %(reference)s')
