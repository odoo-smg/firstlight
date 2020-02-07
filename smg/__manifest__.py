# -*- coding: utf-8 -*-
{
    'name': "SMG - Customizations",

    'summary': """
        This module intend to customize the functions and list to
        Smartrend Manufacturing Group""",

    'description': """
        Customizations performed:

        Products:
            * Product Name:       Validates unique description.
            * Internal Reference: Validates unique code. Mandatory field. Replaces the field name to Product Code.
            * New field: legacy_code - Optional field.
            * New field: revision_code - Optional, it will compose part of the product code.
            * revision_code_onchange - Trigger to fill out the product code.
            * default_nextpart - Defaul pre-filled information into default_code.


        Manufacturing:
            * MRP Produce:
             Validates the selection of the lot and trigger a filter to only lots that have quantity available in stock.


    """,

    'author': "Alexandre Sousa",
    'website': "http://www.smartrendmfg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'depends': ['stock'],
    'depends': ['mrp'],


    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/smg_product_view.xml',
        'views/WebAssetsBackend.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
