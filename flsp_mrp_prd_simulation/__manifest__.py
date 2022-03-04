{
    'name': "FLSP - Production Simulation",

    'summary': """
        Production simulations helps you to visualize the schedule for production 
        based on current availability of the components""",

    'description': """
        Production simulations helps you to visualize the schedule for production 
        based on current availability of the components 
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Manufacture",
    'version': '0.1',
    "depends": ["mrp"],

    # always loaded
    'data': [
        'wizard/flsp_mrp_prd_simulation_wiz.xml',
        'security/ir.model.access.csv',
        'reports/flsp_mrp_prd_simulation_report.xml',
    ],
}
