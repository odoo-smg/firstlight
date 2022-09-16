# -*- coding: utf-8 -*-
{
    'name': "FLSP - Maintenance",

    'summary': """
        Module purpose is to create modifications for maintenance model""",

    'description': """
        Customizations performed:
        
        Equipment:
            * FEB/02 - Added asset # and calibration certificate # on equipment 
            * FEB/02 - Added the two fields on equipment search view
    """,
    'author': "Sami Byaruhanga",
    'website': "http://www.firstlightsafety.com",

    'category': 'maintenance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'maintenance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/flsp_maintenance.xml',
    ],
    'license': 'Other proprietary',
}
