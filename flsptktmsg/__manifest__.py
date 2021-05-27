# -*- coding: utf-8 -*-
{
    'name': "FLSP - Msg",

    'summary': """
        Module purpose is to create ability for user to follow up on ticket""",

    'description': """
        Customizations performed:

        Changes
            * Ticket - added charter 
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
