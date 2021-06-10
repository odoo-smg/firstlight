# -*- coding: utf-8 -*-
{
    'name': "FLSP Automation Module",

    'summary': """This module is designed to run Automation Test """,

    'description': """
        for testing
    """,

    'author': "Perry",
    'website': "http://www.yourcompany.com.ca",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'TestCategory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'board', 'website', 'mrp', 'sale', 'stock', 'delivery'],

    # always loaded
    'data': [
        'views/assets.xml',
    ],
}
