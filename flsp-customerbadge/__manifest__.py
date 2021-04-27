{
    'name': "FLSP - Customer Badge",

    'summary': """
        This module is to customize the badges to customers""",

    'description': """
        Customizations performed:

        Products:
            * Customer:    Add a field Customer Badge.
            * Sales Order: Add a field Customer Badge.
    """,

    'author': "Perry He",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_customer_badge_manage_view.xml',
        'views/flsp_customer_badge_view.xml',
        'views/flsp_customer_view.xml',
        'views/flsp_salesorder_view.xml',
        'views/assets.xml',
    ],
}
