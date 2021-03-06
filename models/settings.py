# settings list

from datetime import timedelta
from constants import FLOW_BASIC, FLOW_MULTIROLE

COMPANY_NAME = 'CtrlPyME'
COMPANY_SLOGAN = 'Press Ctrl + PyME to begin.'
COMPANY_LOGO_URL = URL('static', 'images/ctrlPyME_logo.png')

# the workflow determines how the employees will interact with the application
COMPANY_WORKFLOW = FLOW_BASIC

CASH_OUT_INTERVAL = timedelta(days=1)

EXTRA_FIELD_1_NAME = None
EXTRA_FIELD_2_NAME = None
EXTRA_FIELD_3_NAME = None

# if set true, only those users who have been created by the admin will have access to the online store.
USE_CLIENTS_WHITELIST = True

TICKET_FOOTER = T('This will be a ticket footer... soon')

# PAPER metrics in centimeters
PAPER_WIDTH = 21.59
PAPER_HEIGHT = 27.94
PAPER_MARGIN_TOP = 1
PAPER_MARGIN_RIGHT = 1
PAPER_MARGIN_BOTTOM = 1
PAPER_MARGIN_LEFT = 1

# labels, metrics in centimeters
LABEL_SPACE_X = .5
LABEL_SPACE_Y = .5
LABEL_COLS = 3
LABEL_ROWS = 8
LABEL_SHOW_ITEM_NAME = True
LABEL_SHOW_PRICE = True

PRIMARY_COLOR = '#FFFFFF'
PRIMARY_COLOR_TEXT = '#333333'

ACCENT_COLOR = '#3170F3'
ACCENT_COLOR_TEXT = '#FFFFFF'

BASE_COLOR = '#F3F3F3'
BASE_COLOR_TEXT = '#444'

USE_MATERIAL_ICONS = True

ENABLE_STRIPE = False

TOP_CATEGORIES_STRING = ''

# use it to show the credit notes in the sale ticket, this is useful for people that want to keep the original ticket and print sale ticket with credit note data
MERGE_CREDIT_NOTES_IN_SALE = False


main_settings = db(db.settings.id_store == None).select().first()
if main_settings:
    if main_settings.company_name:
        COMPANY_NAME = main_settings.company_name
    if main_settings.company_slogan:
        COMPANY_SLOGAN = main_settings.company_slogan
    if main_settings.company_logo:
        COMPANY_LOGO_URL = URL('static', 'uploads/'+main_settings.company_logo)
    # if main_settings.workflow:
    #     COMPANY_WORKFLOW = main_settings.workflow
    if main_settings.extra_field_1:
        EXTRA_FIELD_1_NAME = main_settings.extra_field_1
    if main_settings.extra_field_2:
        EXTRA_FIELD_2_NAME = main_settings.extra_field_2
    if main_settings.extra_field_3:
        EXTRA_FIELD_3_NAME = main_settings.extra_field_3

    if main_settings.clients_whitelist:
        USE_CLIENTS_WHITELIST = main_settings.clients_whitelist

    if main_settings.ticket_footer:
        TICKET_FOOTER = main_settings.ticket_footer

    if main_settings.primary_color:
        PRIMARY_COLOR = main_settings.primary_color
    if main_settings.primary_color_text:
        PRIMARY_COLOR_TEXT = main_settings.primary_color_text
    if main_settings.accent_color:
        ACCENT_COLOR = main_settings.accent_color
    if main_settings.accent_color_text:
        ACCENT_COLOR_TEXT = main_settings.accent_color_text
    if main_settings.base_color:
        BASE_COLOR = main_settings.base_color
    if main_settings.base_color_text:
        BASE_COLOR_TEXT = main_settings.base_color_text
    if main_settings.top_categories_string:
        TOP_CATEGORIES_STRING = main_settings.top_categories_string

    if main_settings.cash_out_interval_days:
        CASH_OUT_INTERVAL = timedelta(days=main_settings.cash_out_interval_days)

    if main_settings.merge_credit_notes_in_sale:
        MERGE_CREDIT_NOTES_IN_SALE = True


LABEL_WIDTH = (PAPER_WIDTH - (PAPER_MARGIN_LEFT + PAPER_MARGIN_RIGHT + LABEL_SPACE_X * (LABEL_COLS - 1))) / LABEL_COLS
LABEL_HEIGHT = (PAPER_HEIGHT - (PAPER_MARGIN_TOP + PAPER_MARGIN_BOTTOM + LABEL_SPACE_Y * (LABEL_ROWS - 1))) / LABEL_ROWS


# disable registration if the the store only allows whitelisted clients
if USE_CLIENTS_WHITELIST:
    auth.settings.actions_disabled = ['register']




BASE_BRANDED_EMAIL = """
    <table>
      <tbody>
        <tr> <td><img src="%s" alt=""></td> <td colspan=2><h2>%s</h2></td> </tr>
        {content}
        <tr><td colspan=3>LEGAL thing</td></tr>
      </tbody>
    </table>
""" % (URL('static', 'uploads/' + COMPANY_LOGO_URL, host=True), COMPANY_NAME)

ORDER_EMAIL_CONTENT = '''
    <tr> <td colspan=3><h3>Order {code}</h3></td> </tr>
    <tr> <td colspan=3><h3>Thank you {user_name}</h3></td> </tr>
    <tr><td colspan=3>{order_concept} </td></tr>
    <tr></tr>

    <tr><td colspan=3>'''+ T('Details') +'''</td></tr>
    {items}

    <tr> <td></td> <td>'''+ T('Total') +'''</td> <td>$ {total}</td> </tr>

    <tr><td colspan=3>'''+ T('You can check your orders in') +'<a href="'+ URL('user', 'client_profile') +'"></td></tr>'
