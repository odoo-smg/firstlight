{
    'name': "FLSP GANTT MRP",

    'summary': """
        This module integrates mrp with the interactive HTML5 Gantt chart
        from DHX. Their website is https://dhtmlx.com""",

    "category": "Manufacturing",

    'author': "Alexandre Sousa",
    'website': "https://www.firstlightsafety.com/",
    'license': "GPL-3",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mrp',
        'dhx_gantt'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/production.xml',
    ],
    'qweb': [
        "static/src/xml/gantt.xml",
    ],

    'license': 'Other proprietary',
}
