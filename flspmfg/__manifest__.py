{
    'name': "FLSP - MFG",

    'summary': """
        This module intend to customize the functions and list to
        First Light Safety Products""",

    'description': """
        Customizations performed:

        Production Order:
            * Product: Filter on domain PLM Valid products.
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'depends': ['stock'],
    'depends': ['mrp'],

    # always loaded
    'data': [
        'report/flspmfg_report_mybom_structure.xml',
    ],
}
