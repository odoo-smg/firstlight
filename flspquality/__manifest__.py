# -*- coding: utf-8 -*-
{
    'name': "Flsp - Quality",

    'summary': """
        Module purpose is to control customer issues so as to improve FLSP products.
        """,

    'description': """
        Customizations performed:
            * Jan/25th/2021 - Created the model:
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock', 'mrp'],

    # always loaded
    'data': [
        'security/security.xml',  # create the security groups 1st then add model nxt
        'security/ir.model.access.csv',
        'data/flspqualitydata.xml',
        'views/flspquality.xml',
        'views/flspqualityreason.xml',
        'views/flspqualitystage.xml',
        'views/flspquality_salesorder.xml',
    ],
}
