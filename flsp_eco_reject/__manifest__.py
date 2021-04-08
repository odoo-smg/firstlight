# -*- coding: utf-8 -*-
{
    'name': "FLSP - ECO Reject",

    'summary': """
        To help revert the changes when the product has been rejected
        """,

    'description': """
        Features:
            * Duplicate product on ECO Creation as backup and archive
            * Upon product rejection, revert fields on product to duplicate
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp_plm', 'mrp'],

    # always loaded
    'data': [
        'views/flsp_eco_reject.xml',
    ],

}
