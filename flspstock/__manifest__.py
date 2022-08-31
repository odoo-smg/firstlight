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
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'sale', 'stock', 'delivery', 'deltatech_stock_negative', 'flsppurchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        #'views/flsp_deliveryslip.xml',
        'views/flsp_product_customer_view.xml',
        #'views/flsp_pallet_manifest.xml',
        'views/flsp_stock_package_view_form.xml',
        'views/flsp_stock_picking_form.xml',
        'views/flsp_stock_customer_view_form.xml',
        'views/flsp_mrp_zebra_production.xml',
        #'views/flsp_customer_barcode.xml',
        'views/flsp_stock_zebra_package.xml',
        'views/flsp_product_packaging_form.xml',
        #'views/flsp_mrp_set_zebra_production.xml',
        'views/flsp_stock_production_lot_form.xml',
        #'views/flsp_production_lot_zpl.xml',
        'views/flsp_delivery_wizard.xml',
        'views/package_wizard.xml',
        'views/flsp_production_form.xml',
        'views/flsp_stock_picking_operations.xml',
        #'views/flsp_serial_label_zpl_1x34.xml',
        #'views/flsp_serial_label_zpl_2x1.xml',
        #'views/flsp_antena_lable_zpl_2x1.xml',
        #'views/flsp_stock_package_label_zpl_2x3.xml',
        'views/flsp_stock_track_confirmation.xml',
        'views/flsp_stock_quantity.xml',
        #'views/flsp_stock_inventory.xml',
        'reports/flsp_negative_forecast_report.xml',
        'reports/flsp_negative_forecast_schedule_task.xml',
        'reports/flsp_reservation_report.xml',
        'wizard/flsp_negative_forecast_wizard.xml',
    ],
}
