{
    'name': "FLSP - MRP MTO",

    'summary': """
        Show the needed quantities to produce from Sales Deliveries""",

    'description': """
        Show the needed quantities to produce from Sales Deliveries
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Manufacture",
    'version': '0.1',
    'depends': ['base', "mrp", "stock", "sale"],

    # always loaded
    'data': [
        'views/flsp_mrp_mto.xml',
    ],
    'license': 'Other proprietary',
}
