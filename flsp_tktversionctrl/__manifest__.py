# -*- coding: utf-8 -*-
{
    'name': "FLSP - Version Control",

    'summary': """
           Module purpose is to create version control for ticket system model""",

    'description': """
           Customizations performed:
               * FEB/02 - Added version control model to ticket  
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
        'views/flsp_versionctrl.xml',
    ],
}
