# -*- coding: utf-8 -*-
{
    'name': "FLSP - Tkt Onhold",

    'summary': """
           Module purpose is to put ticket on hold""",

    'description': """
           Customizations performed:
               * FEB/03 - Added on hold on the ticket  
       """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'flspticketsystem'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/flsp_onhold.xml',
        'views/flsp_onholdwizard.xml',

    ],
}
