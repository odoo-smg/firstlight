# -*- coding: utf-8 -*-
{
    'name': "flsp_mrp_sales_report",

    'summary': """
        Sold product report""",

    'description': """

    """,

    'author': "Sami Byaruhanga",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/vending_report.xml',
    ],
    'license': 'Other proprietary',
}
