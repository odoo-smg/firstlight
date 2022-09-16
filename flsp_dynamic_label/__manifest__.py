# -*- coding: utf-8 -*-
{
    'name': "FLSP - Dynamic Labels",

    'summary': """
        To help create dynamic labels that can be called in action wizard
        """,

    'description': """
        Features:
            * Settings: Ability to create Dynamic label templates 
            *           Specify in dynamic label the model to show the template 
            * Specified model: Under actions, dynamic label present on click wizard opens up for user to print label
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'flspautoemails'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_dynamic_label.xml',
        'wizard/flsp_dynamic_label_wizard.xml',
        'views/flsp_dynamic_label_report.xml',
    ],
    "uninstall_hook": "uninstall_hook",

    'license': 'Other proprietary',
}
