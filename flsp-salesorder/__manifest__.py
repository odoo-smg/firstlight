{
    'name': "FLSP - Sales Order",

    'summary': """
        This module intend to customize the functions and list to
        First Light Safety Products""",

    'description': """
        Customizations performed:

        Products:
            * Customer:    Add a field Salesperson 2.
            * Sales Order: Add a field Salesperson 2.
            * Trigger: Trigger Salesperson 2 from Customer to Sales Order.
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.7',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'flsp-base', 'flspstock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_customer_view.xml',
        'views/flsp_salesorder_view.xml',
        'views/flsp_saleorder_listview.xml',
        'views/flsp_account_move_form.xml',
        'views/flsp_stock_picking_form.xml',
    ],
    'license': 'Other proprietary',
}
