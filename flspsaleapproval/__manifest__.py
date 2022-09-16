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
    'depends': ['base', 'sale', 'delivery', 'product', 'flspstock', 'flsp-product', 'flsp-base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_sale_view.xml',
        'views/flsp_sale_settings_view.xml',
        'views/flsp_sale_optional_view.xml',
        'views/flsp_sale_wizard_view.xml',
        'views/flsp_sale_message_view.xml',
        'views/flsp_sale_partner.xml',
        'views/flsp_sale_pricelist_view.xml',
        #'report/flsp_sale_report.xml',
        #'report/flsp_invoice_report.xml',
        #'report/flsp_invoice_report_withoutpay.xml',
        #'report/flsp_commercial_invoice.xml',
        'views/flsp_sppepp_message_view.xml',
        'views/flsp_choose_delivery.xml',
        'views/flsp_reject_wizard_view.xml',
        'views/flsp_confirmed_order_email.xml',
        #'views/flsp_account_move_form.xml',
        'views/flsp_product_category_form.xml',
        'views/flsp_product_template_view_sales.xml',
        'views/flsp_cancel_wizard_view.xml',
        'views/flsp_sale_delivery_message_view.xml',
    ],
    'license': 'Other proprietary',
}
