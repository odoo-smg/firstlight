{
    'name': "FLSP - Purchase MRP",

    'summary': """
        Show the needed quantities to buy and track where the demand came from""",

    'description': """
        Purchase Report that suggests the quantities to buy
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Operations/Purchase",
    'version': '0.1',
    #'depends': ['base', 'mrp', 'sale', 'purchase', 'stock', 'web_progress'],
    'depends': ['base', 'mrp', 'sale', 'purchase', 'stock'],

    # always loaded
    'data': [
        #'wizard/flsp_mrp_purchase_wizard.xml',
        'security/ir.model.access.csv',
        'views/flsp_purchase_mrp.xml',
        'views/flsp_purchase_mrp_line.xml',
    ],
}
