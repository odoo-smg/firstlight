# -*- coding: utf-8 -*-
{
    'name': "FLSP - UOM",

    'summary': """ Prevent to change the UofM""",

    'description': """
        To prevent the user from change a UOM created.
        If needed to edit the user will need to archive and create a new one.
    """,

    'author': "Alexandre Sousa",
    'website': "https://www.firstlightsafety.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase', 'sale', 'purchase_stock'],

    # always loaded
    'data': [
        'views/flsp_uom.xml',
        'views/flsp_uom_category.xml',
    ],
}
