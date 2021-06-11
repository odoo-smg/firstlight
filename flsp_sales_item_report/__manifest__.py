# -*- coding: utf-8 -*-
{
    'name': "FLSP - Sales Item Report",

    'summary': """
        Sales Report by product.""",

    'description': """
        Sales Order - report by item.
    """,
    'author': "Alexandre Sousa",
    'website': "http://www.firstlightsafety.com",

    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'flsp-salesorder'],

    # always loaded
    'data': [
        'views/flsp_sales_item_report.xml',
    ],
}
