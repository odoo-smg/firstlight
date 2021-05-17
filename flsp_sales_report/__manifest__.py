# -*- coding: utf-8 -*-
{
    'name': "FLSP - Sales Report",

    'summary': """
        Sales Report by UTM Source and other.""",

    'description': """
        Customizations performed:
        
        Specification:
            * Sales Order - Add Other Source field.
    """,
    'author': "Alexandre Sousa",
    'website': "http://www.firstlightsafety.com",

    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'utm'],

    # always loaded
    'data': [
        'views/flsp_sales_report_form.xml',
        'views/flsp_crm_team_form.xml',
    ],
}
