# -*- coding: utf-8 -*-
{
    'name': "FLSP - Purchase Lines Report",

    'summary': """
        Purchase Lines Report.""",

    'description': """
        Purchase Lines Report.
    """,
    'author': "Mowahid Latif",
    'website': "http://www.firstlightsafety.com",

    'category': 'purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase'],

    # always loaded
    'data': [
        'views/flsp_po_lines_view.xml',
    ],

    'installable': True,
    'license': 'Other proprietary',
}
