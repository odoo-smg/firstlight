# -*- coding: utf-8 -*-

import logging
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, tools

_logger = logging.getLogger(__name__)


class flspdailysalesorder(models.Model):
    _inherit = 'sale.order'
    _check_company_auto = True

    flsp_email_report_ok = fields.Boolean('Email Report', default=False)

    @api.model
    def _dailysalesorder_email(self):
        template = self.env.ref('flspautoemails.flsp_dailysalesorder_tmpl', raise_if_not_found=False)

        print('**************************sending sales report***************************************')
        if not template:
            print('--------------------------template not found')
            _logger.warning('Template "flspautoemails.flsp_dailysalesorder_tmpl" was not found. Cannot send Daily Sales Order Report.')
            return

        daily_sales = self.env['sale.order'].search(['&', ('state', '=', 'sale'), ('flsp_email_report_ok', '=', False)])
        daily_sales_ids = self.env['sale.order'].search(['&', ('state', '=', 'sale'), ('flsp_email_report_ok', '=', False)]).ids
        daily_sales_line = self.env['sale.order.line'].search([('order_id', 'in', daily_sales_ids)])
        total_sales = self.env['sale.order'].search_count(['&', ('state', '=', 'sale'), ('create_date', '>=', date.today() + relativedelta(days=-1))])

        print('rendered_body')
        rendered_body = template.render({'sales': daily_sales_line, 'total_sales': total_sales}, engine='ir.qweb')
        body = self.env['mail.thread']._replace_local_links(rendered_body)

        if total_sales > 0:
            print('Sending email')
            self.env['mail.mail'].create({
                'body_html': body,
                'subject': 'Daily Sales Order Report',
                'email_to': 'alexandresousa@smartrendmfg.com',
                'auto_delete': True,
            }).send()

        ## Check the sent sales Order
        print('Check the sent sales Order')
        for so in daily_sales:
            so.flsp_email_report_ok = True

        print('************ Daily Sales Order Report - DONE ******************')
