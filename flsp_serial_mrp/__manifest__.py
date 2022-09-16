# -*- coding: utf-8 -*-
{
    'name': "FLSP - Serial MRP",

    'summary': """
        Link Serial/Lots into a MO""",

    'description': """
        Link Serial/Lots into a MO  
    """,

    'author': "Alexandre Sousa",
    'website': "https://www.firstlightsafety.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'mrp', 'sale'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        #'views/production_serial.xml',
        #'views/production_serial_wiz.xml',
        #'views/production_serial_wiz_two.xml',
        #'views/product_product.xml',
        #'views/flsp_serial_mrp_alert_wiz.xml',
    ],
    'license': 'Other proprietary',
}
