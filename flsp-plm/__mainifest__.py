{
    'name': "FLSP - PLM",

    'summary': """
        This module intend to customize the functions and list to
        First Light Safety Products""",

    'description': """
        Customizations performed:

        Products:
            * Product: Add a field ECO enforcement.
            * Product: Add a field PLM Validated.
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'depends': ['stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_product_view.xml',
    ],
}
