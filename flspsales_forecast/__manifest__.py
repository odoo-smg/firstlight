# -*- coding: utf-8 -*-
{
    'name': "FLSP - Sales Forecast",

    'summary': """
        Module purpose is to ease the FLSP planning process for sales""",

    'description': """
        Customizations performed:
        
        Sales forecast:
            * Sales - Add sales forecast 
            * Feb/04/2021 - Added a security group for sales forecast
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock', 'purchase'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/flspsales_forecast.xml',
    ],
}
