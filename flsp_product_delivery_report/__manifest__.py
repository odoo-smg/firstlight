# -*- coding: utf-8 -*-
{
    'name': "flsp_product_delivery_report",

    'summary': """
        Report of delivered products inside a date range.""",

    'description': """
        Added a menu item in manufacturing called "Flsp Delivery Report
        The menu item opens a wizard with two date time fields
        Then returns a tree view of all deliveries between the two date fields"
    """,
    'author': "Kory McCarthy",
    'website': "http://www.firstlightsafety.com",

    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'sale', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_product_delivery_report_view.xml',
        'wizard/delivery_report_wizard_view.xml',

    ],
}
