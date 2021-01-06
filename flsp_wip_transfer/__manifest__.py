{
    'name': "FLSP - WIP Transfer",

    'summary': """
        To facilitate the transfer from WH/Stock to PA/WIP """,

    'description': """
        To facilitate the transfer from WH/Stock to PA/WIP
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Manufacture",
    'version': '0.1',
    'depends': ['base'],
    "depends": ["mrp"],
    "depends": ["product"],
    "depends": ["sale"],
    "depends": ["purchase"],
    "depends": ["stock"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_wip_transfer.xml',
        'wizard/flsp_wip_transfer_wizard.xml',
        'views/flsp_wip_view.xml',
    ],
}
