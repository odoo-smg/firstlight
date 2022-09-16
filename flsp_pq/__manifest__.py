# -*- coding: utf-8 -*-
{
    'name': "FLSP - PQ",

    'summary': """
        Help Specify PQ's""",

    'description': """
        Specify PQ when ordering from a vendor for quality assurance.  
    """,

    'author': "Sami Byaruhanga",
    'website': "https://www.firstlightsafety.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase', 'sale', 'purchase_stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_pq.xml',
        'views/flsp_pqcomment.xml',

    ],
    'license': 'Other proprietary',
}
