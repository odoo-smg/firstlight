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
    'depends': ['mrp'],
    'depends': ['sale'],
    'depends': ['stock'],
    'depends': ['delivery'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_deliveryslip.xml',
        'views/flsp_product_customer_view.xml',
        'views/flsp_pallet_manifest.xml',
        'views/flsp_stock_package_view_form.xml',
        'views/flsp_stock_picking_form.xml',
        'views/flsp_stock_customer_view_form.xml',
        'views/flsp_mrp_zebra_production.xml',
        'views/flsp_customer_barcode.xml',
        'views/flsp_stock_zebra_package.xml',
        'views/flsp_product_packaging_form.xml',
        'views/flsp_mrp_set_zebra_production.xml',
        'views/flsp_stock_production_lot_form.xml',
        'views/flsp_production_lot_zpl.xml',
        'views/flsp_delivery_wizard.xml',
        'views/package_wizard.xml',
    ],
}
