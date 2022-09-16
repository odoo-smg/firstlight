{
    'name': "FLSP - MRP Batch Produce",

    'summary': """
        Create Serial Numbers before completing the MO""",

    'description': """
        Include a field on the MO to link the batch Serial Numbers.
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Manufacture",
    'version': '0.1',
    'depends': ['base', 'mrp', 'stock', 'flspserialnum'],

    # always loaded
    'data': [
        #'views/flsp_mrp_batch.xml',
        #'views/flsp_mrp_production.xml',
        #'views/flsp_mrp_produce.xml',
        #'views/flsp_report_mrporder.xml',
    ],
    'license': 'Other proprietary',
}
