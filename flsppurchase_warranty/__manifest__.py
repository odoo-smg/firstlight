# -*- coding: utf-8 -*-
{
    'name': "FLSP - Purchase Warranty",

    'summary': """
        Model purpose is to handle FLSP purchase warranty""",

    'description': """
        Customizations performed:
            * Feb/10th/2021/W - Purchase form: added warranty button check box
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/flsppurchase_warranty.xml',
    ],
    'license': 'Other proprietary',
}
