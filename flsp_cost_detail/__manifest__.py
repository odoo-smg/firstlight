# -*- coding: utf-8 -*-
{
    'name': "FLSP Cost Detail",

    'summary': """
        This module intend to customize the functions and list to
        Smartrend Manufacturing Group""",

    'description': """
        Customizations performed:

        Products:
            * Included a button to show the cost detail report

        Cost Detail Report

    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.4',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_automation', 'stock', 'sale', 'purchase', 'mrp', 'stock_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_cost_detail_product_tmpl.xml',
        'views/flsp_cost_detail.xml',
    ],
}
