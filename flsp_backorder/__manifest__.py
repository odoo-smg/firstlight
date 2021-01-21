# -*- coding: utf-8 -*-
{
    'name': "flsp_backorder",

    'summary': """
        To write back order status to done
                """,

    'description': """
    Inherits the stock picking model so as to write the state to done when backorder is created
    """,

    'author': "Sami Byaruhanga",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'sale', 'stock', 'delivery'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
}
