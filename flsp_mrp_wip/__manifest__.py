{
    'name': "FLSP - MRP WIP",

    'summary': """
        WIP Transfer from the MO""",

    'description': """
        Include a button in the MO to create an internal transfer from Stock to WIP
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Manufacture",
    'version': '0.1',
    'depends': ['base', 'mrp', 'stock', 'flsp_pdct_standard_location'],

    # always loaded
    'data': [
        'views/flsp_mrp_wip_wiz.xml',
        'views/flsp_production.xml',
    ],
}
