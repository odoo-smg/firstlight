{
    'name': "FLSP - ECO",

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
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'depends': ['stock'],
    'depends': ['mrp'],
    'depends': ['mrp_plm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_producteco_view.xml',
        'views/flsp_eco_view.xml',
        'views/flsp_eco_stage_view.xml',
    ],
}
