{
    'name': "FLSP Sale Target",

    'summary': """
        To create a sales target by product category """,

    'description': """
        Customizations performed:

        Product Category:
            * Creates a list of sales target by month.
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_category_target.xml',
        'views/partner_tags.xml',
    ],
    'license': 'Other proprietary',
}
