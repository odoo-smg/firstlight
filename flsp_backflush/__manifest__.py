# -*- coding: utf-8 -*-
{
    'name': "flsp_backflush",

    'summary': """
        To backflush the components transferred previously into PA/WIP
                """,

    'description': """
    Verifies the quantity transferred and the quantity consumed by the MO to remove the difference from PA/WIP.
    """,

    'author': "Alexandre Sousa",
    'website': "www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'sale', 'stock', 'delivery'],

    # always loaded
    'data': [
        'views/backflush_products.xml',
        'views/backflush_production.xml',
        #'views/production.xml',
    ],
}
