# -*- coding: utf-8 -*-
{
    'name': "FLSP - BOM Availability",

    'summary': """
    Module purpose is to show the BOM quantity on hand and forecast""",

    'description': """
        * Mar.1st.2021 - Created the model
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'flsp_purchase_mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_bom_availability_view.xml',
        'wizard/flsp_bom_availability_wizard.xml',

    ],
    'license': 'Other proprietary',
}
