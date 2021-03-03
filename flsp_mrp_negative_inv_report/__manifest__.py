# -*- coding: utf-8 -*-
{
    'name': "FLSP - MRP Negative Inventory Report",

    'summary': """
        Module purpose is to create a Negative Inventory Report.
        """,

    'description': """
        Customizations performed:
            * Mar/1st/2021 - Created the model:
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_negative_inv.xml',
    ],
}
