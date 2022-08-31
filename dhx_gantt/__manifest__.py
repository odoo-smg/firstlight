{
    'name': "Mediocre DHX Gantt",

    'summary': """
        This module integrates project tasks with the interactive HTML5 Gantt chart
        from DHX. Their website is https://dhtmlx.com""",

    "category": "Project Management",

    'author': "Ubay Abdelgadir",
    'website': "https://github.com/obayit/odoo_dhtmlxgantt",
    'license': "GPL-3",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Project Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'project'
    ],
    'assets': {
            'web.assets_backend': [
                '/dhx_gantt/static/lib/dhtmlxgantt/js/dhtmlxgantt.js',
                '/dhx_gantt/static/lib/dhtmlxgantt/js/dhtmlxgantt_marker.js',
                '/dhx_gantt/static/lib/dhtmlxgantt/skins/dhtmlxgantt_material.css',
                '/dhx_gantt/static/src/js/gantt_model.js',
                '/dhx_gantt/static/src/js/gantt_renderer.js',
                '/dhx_gantt/static/src/js/gantt_controller.js',
                '/dhx_gantt/static/src/js/gantt_view.js',
                '/dhx_gantt/static/src/js/gantt_action.js',
                '/dhx_gantt/static/src/css/gantt.css',
            ],
        },

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        #'views/assets.xml',
        'views/task_views.xml',
        'views/project_views.xml',
    ],
    'qweb': [
        "static/src/xml/gantt.xml",
    ],
    'images': [
        'images/screenshot_1.png'
    ],
    'uninstall_hook': 'dhx_uninstall_hook'

}
