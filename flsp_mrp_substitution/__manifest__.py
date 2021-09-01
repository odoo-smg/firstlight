# -*- coding: utf-8 -*-
{
    'name': "FLSP - MRP Substitution",

    'summary': """
        Module purpose is to create Product substitution on Manufacturing orders 
        """,

    'description': """
        Customizations performed:
            * Manufacturing - Substitute component on manufacturing line 
            * Product temp  - Add many2many products on the template for substitution
            * Mrp BOM line  - Show check box if product has substitution
    """,

    'author': "Alexandre Sousa",
    'website': "http://www.firstlightsafety.com",

    'category': 'mrp',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'stock', 'flsp-mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/flsp_mrp_substitution_wiz.xml',
        'views/flsp_mrp_substitution_bom_line.xml',
        'views/flsp_mrp_substitution_production.xml',
        'views/flsp_mrp_substitution_tree_raw_mo.xml',
        'views/flsp_mrp_substitution_change_prod_qty_wiz.xml',
    ],
}
