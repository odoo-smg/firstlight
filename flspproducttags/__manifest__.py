# -*- coding: utf-8 -*-
{
    'name': 'FLSP - Product tags',
    'summary': 'Allows to add tags to FLSP - products',
    'description':
        """
        Module allows you to distinguish your products with tags \n
        1. Can set own tags 
        2. Can search products with tags specified
        """,

    'author': ' ',
    'website': 'http://',
    'category': 'Generic Modules/Manufacturing',
    'version': '1.0',
    # 'sequence': 1,

    'depends': ['base', 'product', 'mrp'], #'sale_management',
    'data': [
        'security/tags_security.xml',
        'security/ir.model.access.csv',
        'views/product_tags.xml',
        'views/product_template.xml',
        ],
}


