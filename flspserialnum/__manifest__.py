# -*- coding: utf-8 -*-
{
    'name': "FLSP - Serial Number",

    'summary': """
        Module purpose is to create multiple serial numbers and print in batch""",

    'description': """
        Customizations performed:
            * Manufacturing - Print multiple serial numbers
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
        'views/flspserialnum.xml',
        'views/flspserialnum_pdf.xml',
        'views/flspserialnum_zebra.xml',
        'views/flspserialnum_zpl_1x34.xml',
        'views/flspserialnum_zpl_2x1.xml',
        'views/flspantena_zpl_2x1.xml',
    ],
}
