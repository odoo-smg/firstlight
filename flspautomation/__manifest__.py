# -*- coding: utf-8 -*-
{
    'name': "FLSP Automation Test Module",

    'summary': """This module is designed to run Automation Test and provide functions referred by tests in other modules.""",

    'description': """
        This module is designed to run Automation Test and provide functions referred by tests in other modules.
    """,

    'author': "Perry He",
    'website': "http://www.smartrendmfg.com",

    'category': 'AutomationTest',
    'version': '0.1',

    'depends': ['base', 'sale', 'purchase', 'mrp', 'stock', 'flsp-product'],

    'data': [
        'views/assets.xml',
    ],
    'license': 'Other proprietary',
}
