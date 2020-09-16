# -*- coding: utf-8 -*-
{
    'name': "FLSP - Ticket system",
    'summary': """Task Management""",
    'description': """
        Ticketing System to help simplify user requests for changes to the ERP/IT team.
            -Send tasks to the ERP Developers and IT support team
            
    """,
    'author': "Sami Byaruhanga",
    'website': "http://",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sept_4th',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    # 'depends': ['mail', 'contacts'],

    # always loaded
    'data': [
        'security/security.xml',  # create the security groups 1st then add model nxt
        'security/ir.model.access.csv',
        'views/ticket.xml',
        'views/category.xml',
        'demo/demo.xml',
        # 'views/mail_template.xml',

    ],
    # # only loaded in demonstration mode
    # 'demo': [
    #     # 'demo/demo.xml',
    # ],

  }
