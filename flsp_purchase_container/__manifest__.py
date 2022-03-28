{
    'name': "FLSP Purchase Container",

    'summary': """
        To manage the overseas container """,

    'description': """
        Customizations performed:

        - Container
        - Receipt: new field container 
                   prevents the receipt to be completed.
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    'category': 'Other',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase', 'mail', 'purchase_stock'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/flsp_purchase_container.xml',
        'views/flsp_purchase_container_stock_picking.xml',
        'wizard/flsp_purchase_container_stock_picking_wiz.xml',
        'wizard/flsp_purchase_container_po_wiz.xml',
        'wizard/flsp_purchase_container_po_line_wiz.xml',
    ],
}
