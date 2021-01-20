# -*- coding: utf-8 -*-
{
    'name': "FLSP - Bom Compare",

    'summary': """
    Module purpose is to compare BOMs""",

    'description': """
    Customizations performed:
    Bom Compare:
        * MRP - Compare BOMs 
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_comparebom_view.xml',
        'wizard/flsp_comparebom_wizard.xml',

    ],
}
