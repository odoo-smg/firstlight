# -*- coding: utf-8 -*-
{
    'name': "SMG - Sandbox Background",

    'summary': """
        This module intend to change the background color
        Smartrend Manufacturing Group""",

    'description': """
        Customizations performed:

        Applies only to Sandbox environment
        Change the default background color: Apply only in Sandbox environment

    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.4',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'depends': ['web'],

    # always loaded
    'data': [
        'views/WebAssetsBackend.xml',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/WebAssetsBackend.xml',
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
}
