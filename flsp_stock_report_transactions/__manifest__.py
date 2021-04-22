{
    'name': "FLSP - Stock Report Transactions",

    'summary': """
        (Stock Kardex) Show all the transactions for a product and its balance by date""",

    'description': """
        (Stock Kardex) Show all the transactions for a product and its balance by date
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",
    "category": "Stock",
    'version': '0.1',
    'depends': ['base'],
    "depends": ["mrp"],
    "depends": ["sale"],
    "depends": ["purchase"],
    "depends": ["stock"],

    # always loaded
    'data': [
        'wizard/flsp_stock_report_transactions_wizard.xml',
        'reports/flsp_stock_report_transactions.xml',
    ],
}
