# -*- coding: utf-8 -*-
{
    'name': "FLSP - Account Currency",

    'summary': """
        Show original values before conversion to CAD
                """,

    'description': """
    This module will change the forms and views to show original values before exchange rate of CAD is applied
    """,

    'author': "Alexandre Sousa",
    'website': "www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'views/account_move.xml',
    ],
}
