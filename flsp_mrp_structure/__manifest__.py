{
    'name': "FLSP - MRP Structure",

    'summary': """
        Show the needed quantities to complete the MO and track WHEN the components will arrive""",

    'description': """
        Show the needed quantities to complete the MO and track WHEN the components will arrive
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Manufacture",
    'version': '15.1',
    'depends': [],

    # always loaded
    'data': [
        #'views/flsp_mrp_structure.xml',
        #'views/production_form_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/flsp_mrp_structure/static/src/js/report_flsp_structure.js',
            '/flsp_mrp_structure/static/src/scss/flsp_mrp_structure.scss',
        ],
    },
    'qweb': ['static/src/xml/flsp_mrp.xml'],
    'license': 'Other proprietary',
}
