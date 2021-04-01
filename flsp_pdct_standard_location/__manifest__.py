# -*- coding: utf-8 -*-
{
    'name': "FLSP - Standard Product Location",

    'summary': """
        Useful in adding standard location on product (template and product)""",

    'description': """ Changes
            * Mar.31st.2021 - Created the model 
        """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/flsp_pdct_standard_location.xml',
    ],
}
