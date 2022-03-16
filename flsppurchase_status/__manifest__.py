# -*- coding: utf-8 -*-
{
    'name': "flsppurchase_status",

    'summary': """
            FLSP Purchase customizations
            """,

    'description': """
        Following customizations are made on the Purchase Model to meet FLSP Standards\n
        1. FLSP Status (Oct/29th/Thur/2020)
            -Added flsp status: request(yellow), non-confirmed(yellow), confirmed(green), received(gray), late(red)\n
            -Added fields on PO Form: flsp_vendor_date, flsp_scheduled_date
            -flsp_scheduled date linked with the receipt scheduled date
            -Added Payment terms linked with the accounting payment terms
        2. Flsp_delivery_address (Nov/16th/Mon/2020) on company
        3. Drop ship address added on flsp_po_print.xml line 137 for PO and LINE 527 RFQ (Feb/10th/W/2021)
    """,

    'author': "Sami Byaruhanga",

    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'sale', 'stock', 'purchase_stock', 'flspautomation'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/flsp_po_print.xml', #for printing PO to FLSP Standards
        'views/flsp_po_status.xml', #for adding status in tree and dates in form
        'views/flsp_delivery_address.xml', #for adding the delivery address
        'views/flsp_approve_po_wiz.xml',
        'views/flsp_reject_po_wiz.xml',
        'security/flsp_user_group.xml',
        'views/flsppurchase_status_stock_picking.xml',
    ],
}
