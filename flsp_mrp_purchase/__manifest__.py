{
    'name': "FLSP - MRP Purchase",

    'summary': """
        Show the needed quantities to produce and track where the demand came from""",

    'description': """
        Show the needed quantities to produce and track where the demand came from
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Manufacture",
    'version': '0.1',
    'depends': ['base', 'mrp', 'sale', 'purchase', 'stock'],

    # always loaded
    'data': [
        'wizard/flsp_mrp_purchase_wizard.xml',
        'reports/flsp_mrp_purchase_report.xml',
        'security/ir.model.access.csv',
        'views/flsp_mrp_purchase_line.xml',
        'views/flsp_product_mrp_purchase.xml',
    ],
}
