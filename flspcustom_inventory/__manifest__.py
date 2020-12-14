# -*- coding: utf-8 -*-
{
    'name': "FLSP - Custom Inventory",

    'summary': """
        This model contains all customizations to inventory existing forms""",

    'description': """
        Customizations performed:
        Dec/14th/2020:
            * Default filter for update quantity is internal locations.
    """,

    'author': "Sami Byaruhanga",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'sale', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/filter.xml',
        # 'views/templates.xml',
    ],
}
