# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'FLSP Accounting Reports',
    'summary': 'View and create reports',
    'category': 'Accounting/Accounting',
    'description': """
FLSP Accounting Reports
==================
    """,
    'depends': ['account_accountant'],

    'assets': {
            'web.assets_backend': [
                '/flsp_account_reports/static/src/js/mail_activity.js',
                '/flsp_account_reports/static/src/js/account_reports.js',
                '/flsp_account_reports/static/src/js/action_manager_account_report_dl.js',
                '/flsp_account_reports/static/src/scss/account_financial_report.scss',
                '/dhx_gantt/static/src/js/gantt_renderer.js',
                '/dhx_gantt/static/src/js/gantt_controller.js',
                '/dhx_gantt/static/src/js/gantt_view.js',
                '/dhx_gantt/static/src/js/gantt_action.js',
                '/dhx_gantt/static/src/css/gantt.css',
            ],
        },


    'data': [
        'security/ir.model.access.csv',
        'data/account_financial_report_data.xml',
        'views/assets.xml',
        'views/account_report_view.xml',
        'views/report_financial.xml',
        'views/search_template_view.xml',
        'views/partner_view.xml',
        'views/account_journal_dashboard_view.xml',
        'views/res_config_settings_views.xml',
        #'wizard/report_export_wizard.xml',
        #'wizard/fiscal_year.xml',
        #'views/account_activity.xml',
        #'views/vendor_reference_report_view.xml',
    ],
    'qweb': [
        'static/src/xml/account_report_template.xml',
    ],
    'auto_install': True,
    'installable': True,
    'license': 'OEEL-1',
    'post_init_hook': 'set_periodicity_journal_on_companies',
}
