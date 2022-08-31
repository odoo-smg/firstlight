{
    'name': "FLSP - MRP",

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
    'depends': ['base', 'stock', 'mrp', 'mrp_plm'],
    'depends': ['flspstock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_bom_view.xml',
        'views/flsp_bom_products_view.xml',
        'views/flsp_production_wizard_msg.xml',
        'views/flsp_production_view.xml',
        #'views/flsp_stock_move_view.xml',
        'views/flsp_mrp_negative_forecast_view.xml',
        'report/flsp_production_component_finished.xml',
        'report/flsp_production_components.xml',
        'views/flsp_mrp_comp_warning_wiz.xml',
        'security/flsp_user_group.xml',
        'data/flsp_automation.xml',
        'views/flsp_product_form.xml',
    ],
}
