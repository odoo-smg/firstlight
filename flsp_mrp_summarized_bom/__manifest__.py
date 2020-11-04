{
    'name': "FLSP - Summarized BOM",

    'summary': """
        Summarized BOM, chose one or more products and inform the quantity to see the 
        list of components summarized""",

    'description': """
        Summarized BOM, chose one or more products and inform the quantity to see the 
        list of components summarized. 
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Manufacture",
    'version': '0.1',
    "depends": ["mrp"],

    # always loaded
    'data': [
        'wizard/flsp_summarized_bom_view.xml',
        'security/ir.model.access.csv',
        'reports/flsp_summarized_bom_report.xml',
    ],
}
