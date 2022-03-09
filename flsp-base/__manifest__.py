{
    'name': "FLSP - Base",

    'summary': """
        This module intend to fix the problem with dependencies
        First Light Safety Products""",

    'description': """
        Customizations performed:
        copied the fields from other modules in order to solve dependency issues
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'delivery'],

    # always loaded
    'data': [
    ],
}
