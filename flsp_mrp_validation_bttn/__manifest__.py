# -*- coding: utf-8 -*-
{
    'name': "FLSP - MRP Validation Button",

    'summary': """
        To add MRP Validation button on the product template and manufacturing process.
        """,

    'description': """
        Features:
            * MRP Validation Security access group in settings
            * MRP Validation button on product template
            * MRP and PLM validation errors rise once the product is not MRP or PLM validated respectively
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",
    'category': 'Manufacturing/Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/flsp_mrp_validation_bttn.xml',
    ],
}
