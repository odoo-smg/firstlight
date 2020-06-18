{
    'name': "FLSP - Inventory",

    'summary': """
        - FLSP Delivery Slip
        """,

    'description': """
        Customizations performed:

        Inventory:
            * FLSP - Packing Slip.
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
    'depends': ['delivery'],

    # always loaded
    'data': [
        'views/flsp_deliveryslip.xml',
    ],
}
