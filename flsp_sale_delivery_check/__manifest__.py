{
    'name': "FLSP - Sales Delivery Check",

    'summary': """
        Show the Sales Order by Delivery and track production""",

    'description': """
        Show the Sales Order by Delivery and track production
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Sales",
    'version': '0.1',
    'depends': ['base', "mrp", "stock", "sale", "flsp_mrp_mto"],

    # always loaded
    'data': [
        'views/flsp_sale_delivery_check.xml',
    ],
}
