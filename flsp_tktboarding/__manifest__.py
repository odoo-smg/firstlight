# -*- coding: utf-8 -*-
{
    'name': "FLSP - Ticket Boarding",

    'summary': """
           Useful for creating on and off boarding tickets""",

    'description': """
           Features:
               * Apr/22 - Ability to create tickets in HR for employees boarding process
               * Apr/23 - Ability to remove assigned from the ticket form view
       """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'flspticketsystem', 'hr'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_tktboarding.xml',
        'views/flsp_removeassign.xml',
        #'demo/demo.xml',
        'wizard/employee_wizard.xml',
        'wizard/employee_inherit.xml',
    ],
}
