# -*- coding: utf-8 -*-
{
    'name': "FLSP - Specification",

    'summary': """
        Module purpose is to create product specification""",

    'description': """
        Customizations performed:
        Specification:
            * Manufacturing - Add specification to products 
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock', 'purchase', 'product', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_specification.xml',
        'views/pdct_temp.xml',
    ],
}
