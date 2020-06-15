{
    'name': "FLSP - Sale Approval",

    'summary': """
        This module intend to customize the functions and list to
        First Light Safety Products""",

    'description': """
        Customizations performed:

        Sales:
            * Discount approval.
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
    'depends': ['sale'],
    'depends': ['delivery'],

    # always loaded
    #'views/flsp_sale_settings_view.xml',
    'data': [
        'views/flsp_sale_view.xml',
        'views/flsp_sale_optional_view.xml',
        'views/flsp_sale_wizard_view.xml',
        'views/flsp_sale_message_view.xml',
        'views/flsp_sale_partner.xml',
        'views/flsp_sale_pricelist_view.xml',
        'report/flsp_sale_report.xml',
        'report/flsp_invoice_report.xml',
        'report/flsp_invoice_report_withoutpay.xml',
        'views/flsp_sppepp_message_view.xml',
    ],
}
