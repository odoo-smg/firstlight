{
    'name': "FLSP - MRP Simulation",

    'summary': """
        Show the MRP simulation to produce and compare Required Qty and On Hand Qty
    """,

    'description': """
        Show the MRP simulation to produce and compare Required Qty and On Hand Qty
    """,

    'author': "Perry He",
    'website': "http://www.smartrendmfg.com",
    "category": "Manufacture",
    'version': '0.1',
    'depends': ['base', 'mrp', 'stock', 'sale', 'purchase', 'flsp-product'],
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_mrp_simulation.xml',
    ],
    'license': 'Other proprietary',
}
