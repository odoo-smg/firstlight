# -*- coding: utf-8 -*-
{
    'name': "FLSP - MRP Filter SN",

    'summary': """
        Module purpose is to show only available Serial numbers on the production, produce wizard""",

    'description': """
        Customizations performed:

        Changes
            * Mar.26th.2021 - Created the model
            * Apr.8th.2021 - Filter SN for all internal transfers
            * Apr.15th.2021 - Modified the model to filter for both the lots and SN
            * Apr.15th.2021 - Create scheduled action if you wish to call check_all_available_sn in stock.production.lot
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/flsp_mrp_filter_sn.xml',
    ],
}
