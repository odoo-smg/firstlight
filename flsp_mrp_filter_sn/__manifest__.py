# -*- coding: utf-8 -*-
{
    'name': "FLSP - MRP Filter SN",

    'summary': """
        Module purpose is to show only available Serial numbers on the production, produce wizard""",

    'description': """ Changes
            * Mar.26th.2021 - Created the model 
            * Apr.8th.2021  - Filter SN for all internal transfers
        """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/flsp_mrp_filter_sn.xml',
    ],
}
