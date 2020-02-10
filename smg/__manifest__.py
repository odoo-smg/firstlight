# -*- coding: utf-8 -*-
{
    'name': "SMG - Sandbox background",

    'summary': """
        This module intend to change the background color
        Smartrend Manufacturing Group""",

    'description': """
        Customizations performed:

        Applies only to Sandbox environment
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/WebAssetsBackend.xml',
    ],
}
