# -*- coding: utf-8 -*-
{
    'name': "FLSP - Stock Request",

    'summary': """
        Module purpose is assist manufacturing team to request products from material planners""",

    'description': """
        Customizations performed:
        
        Stock request:
            * Stock Request from the manufacturing team to the Material Planner
            * Material Handler will create internal transfers of the products.
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    'category': 'mrp',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flspstockrqst.xml',
    ],
}
