{
    'name': "FLSP - Purchase",

    'summary': """
        This module intend to customize the functions and list to
        First Light Safety Products""",

    'description': """
        Customizations performed:

        Purchase Order:
            * Add a field on Quote Lines = Vendor Product Code.
            * Add a button on Products to show open POs.
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'depends': ['purchase'],
    'depends': ['sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_purchase_view.xml',
        'views/flsp_product_view.xml',
        'views/flsp_purchase_order_line_view.xml',
        'views/flsp_suggestion_wizard.xml',
        'report/flsp_purchase_suggestion.xml',
        'views/flspterms.xml',
        #'views/flspterms_vendor.xml',
        'report/flsp_po_print.xml',
    ],
}
