{
    'name': "FLSP - WORK CENTER",

    'summary': """
        Work Centers to group MOs""",

    'description': """
        Includes a field for custom work center at the MO and creates cards to access the MOs.
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Manufacture",
    'version': '0.1',
    'depends': ['base', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_mrp_work_center.xml',
        'views/flsp_mrp_mo.xml',
    ],
}
