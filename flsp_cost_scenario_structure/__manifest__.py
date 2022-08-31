{
    'name': "FLSP - Cost Scenario Structure",

    'summary': """
        Show the cost for the BOM and track historical cost""",

    'description': """
        Show the cost for the BOM and track historical cost
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Manufacture",
    'version': '0.1',
    'depends': ['base', 'mrp', 'sale', 'purchase', 'stock'],

    'assets': {
        'web.assets_backend': [
            '/flsp_cost_scenario_structure/static/src/js/report_cost_scenario_structure.js"',
            '/flsp_cost_scenario_structure/static/src/scss/flsp_cost_scenario_structure.scss',
        ],
    },


    # always loaded
    'data': [
        'views/flsp_cost_scenario_structure.xml',
        'views/flsp_bom_form_view.xml',
    ],
    'qweb': ['static/src/xml/flsp_cost_scenario_structure.xml'],
}
