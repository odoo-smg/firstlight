# -*- coding: utf-8 -*-

import logging
from datetime import date, datetime
from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class flspdailysalesorder(models.Model):
    _inherit = 'sale.order'
    _check_company_auto = True

    flsp_email_report_ok = fields.Boolean('Email Report', default=False, copy=False)
    flsp_so_date = fields.Date('SO Date', default=False, copy=False)

    @api.model
    def _dailysalesorder_email(self):
        template = self.env.ref('flspautoemails.flsp_dailysalesorder_tmpl', raise_if_not_found=False)

        if not template:
            _logger.warning('Template "flspautoemails.flsp_dailysalesorder_tmpl" was not found. Cannot send Daily Sales Order Report.')
            return

        daily_sales = self.env['sale.order'].search(['&', ('state', 'in', ['sale', 'done']), ('flsp_email_report_ok', '=', False)])
        total_sales = self.env['sale.order'].search_count(['&', ('state', 'in', ['sale', 'done']), ('flsp_email_report_ok', '=', False)])
        daily_sales_ids = self.env['sale.order'].search(['&', ('state', 'in', ['sale', 'done']), ('flsp_email_report_ok', '=', False)]).ids
        daily_sales_line = self.env['sale.order.line'].search([('order_id', '=', daily_sales_ids)])

        rendered_body = template.render({'sales': daily_sales_line, 'total_sales': total_sales}, engine='ir.qweb')
        body = self.env['mail.thread']._replace_local_links(rendered_body)

        if total_sales > 0:
            self.env['mail.mail'].create({
                'body_html': body,
                'subject': 'Daily Sales Order Report',
                'email_to': 'alexandresousa@smartrendmfg.com; camquan@smartrendmfg.com; soniastachurska@smartrendmfg.com',
                'auto_delete': True,
            }).send()
            ## Check the sent sales Order
            for so in daily_sales:
                so.flsp_email_report_ok = True
                so.flsp_so_date = datetime.now()

    @api.model
    def _weeklysalesorder_email(self):
        template = self.env.ref('flspautoemails.flsp_weeklysalesorder_tmpl', raise_if_not_found=False)

        if not template:
            _logger.warning('Template "flspautoemails.flsp_dailysalesorder_tmpl" was not found. Cannot send Daily Sales Order Report.')
            return

        weekly_report = self.pool.get('report.flspautoemails.flsp_weeklysalesorder_report')
        sale_ids = self.search([], limit=1).ids
        data = weekly_report._get_report_values(self, sale_ids)

        rendered_body = template.render({'total_sales_by_month': data['total_sales_by_month'],
                                         'sale_by_person': data['sale_by_person'],
                                         'd_to': data['d_to'],
                                         'd_from': data['d_from']}, engine='ir.qweb')

        body = self.env['mail.thread']._replace_local_links(rendered_body)
        body += '<br/><br/><br/>'
        body += '<div style = "text-align: center;" >'
        body += '  <a href = "https://odoo-smg-firstlight1.odoo.com/web#action=408&amp;model=sale.order&amp;view_type=list&amp;cids=1&amp;menu_id=230" style = "background: #1abc9c; padding: 20px; text-decoration: none; color: #fff; border-radius: 5px; font-size: 16px;" class ="o_default_snippet_text">Access Sales Order</a>'
        body += '  <br/><br/><br/>'
        body += '</div>'
        body += '<p>Thank you!</p>'

        self.env['mail.mail'].create({
            'body_html': body,
            'subject': 'Weekly Sales Order Report',
            'email_to': 'alexandresousa@smartrendmfg.com; camquan@smartrendmfg.com',
            'auto_delete': True,
        }).send()

    @api.model
    def _weeklysalesorder_report(self):
        sale_ids = self.search([], limit=1).ids
        return self.env.ref('flspautoemails.flsp_weeklysalesorder_report').report_action(sale_ids)

    @api.model
    def _apprvreq_email(self):
        template = self.env.ref('flspautoemails.flsp_soapprovreq_tmpl', raise_if_not_found=False)
        if not template:
            _logger.warning('Template "flspautoemails.flsp_soapprovreq_tmpl" was not found. Cannot send Approval Request Report.')
            return

        total_sales = self.env['sale.order'].search_count([('flsp_state', '=', 'wait')])
        docids = self.env['sale.order'].search([('flsp_state', '=', 'wait')])
        d_from = date.today()

        rendered_body = template.render({'docids': docids,
                                         'd_from': d_from}, engine='ir.qweb')

        body = self.env['mail.thread']._replace_local_links(rendered_body)
        body += '<br/><br/><br/>'
        body += '<div style = "text-align: center;" >'
        body += '  <a href = "/web#action=408&amp;model=sale.order&amp;view_type=list&amp;cids=1&amp;menu_id=230" style = "background: #1abc9c; padding: 20px; text-decoration: none; color: #fff; border-radius: 5px; font-size: 16px;" class ="o_default_snippet_text">Access Sales Order</a>'
        body += '  <br/><br/><br/>'
        body += '</div>'
        body += '<p>Thank you!</p>'

        if total_sales > 0:
            self.env['mail.mail'].create({
                'body_html': body,
                'subject': 'Odoo - Sales Discount Approval Request Reminder',
                'email_to': 'camquan@smartrendmfg.com;stephanieaddy@smartrendmfg.com; ',
                'auto_delete': True,
            }).send()

    @api.model
    def _soapprovreq_report(self, sale_orders=None):
        if not sale_orders:
            sale_orders = self.env['sale.order'].search([('flsp_state', '=', 'wait')]).ids
            if len(sale_orders) == 0:
                sale_orders = [0]

        return self.env.ref('flspautoemails.flsp_soapprovreq_report').report_action(sale_orders)
