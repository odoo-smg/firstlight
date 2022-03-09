{
    'name': "FLSP - Accounting",

    'summary': """
        This module intend to customize the functions and list to
        First Light Safety Products""",

    'description': """
        Customizations performed:

        Partner:
            * Accounting Validated field to enforce validation.
            * Sales Orders: Filter accounting validated partners.
            * Purchase Orders: Filter accounting validated partners.
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'purchase', 'flsp-base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_partner_view.xml',
        'views/flsp_credit_report.xml',
    ],
}
