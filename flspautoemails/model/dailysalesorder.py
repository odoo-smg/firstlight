# -*- coding: utf-8 -*-

import logging
import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, tools

_logger = logging.getLogger(__name__)


class flspdailysalesorder(models.Model):
    _inherit = 'sale.order'
    _check_company_auto = True

    flsp_email_report_ok = fields.Boolean('Email Report', default=False, copy=False)
    flsp_so_date = fields.Date('SO Date', default=False, copy=False)

    @api.model
    def _dailysalesorder_email(self):
        print('**************************sending sales report***************************************')
        template = self.env.ref('flspautoemails.flsp_dailysalesorder_tmpl', raise_if_not_found=False)

        print('**************************checking template***************************************')
        if not template:
            print('--------------------------template not found')
            _logger.warning('Template "flspautoemails.flsp_dailysalesorder_tmpl" was not found. Cannot send Daily Sales Order Report.')
            return

        daily_sales = self.env['sale.order'].search(['&', ('state', '=', 'sale'), ('flsp_email_report_ok', '=', False)])
        total_sales = self.env['sale.order'].search_count(['&', ('state', '=', 'sale'), ('flsp_email_report_ok', '=', False)])
        daily_sales_ids = self.env['sale.order'].search(['&', ('state', '=', 'sale'), ('flsp_email_report_ok', '=', False)]).ids
        daily_sales_line = self.env['sale.order.line'].search([('order_id', '=', daily_sales_ids)])

        print('rendered_body')
        rendered_body = template.render({'sales': daily_sales_line, 'total_sales': total_sales}, engine='ir.qweb')
        body = self.env['mail.thread']._replace_local_links(rendered_body)

        if total_sales > 0:
            print('Sending email')
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


        print('************ Daily Sales Order Report - DONE ******************')
    @api.model
    def _weeklysalesorder_email(self):
        template = self.env.ref('flspautoemails.flsp_weeklysalesorder_tmpl', raise_if_not_found=False)

        print('**************************sending sales report***************************************')
        if not template:
            print('--------------------------template not found')
            _logger.warning('Template "flspautoemails.flsp_dailysalesorder_tmpl" was not found. Cannot send Daily Sales Order Report.')
            return

        daily_sales = self.env['sale.order'].search(['&',
                                                     ('state', '=', 'sale'),
                                                     ('flsp_so_date', '>', date.today() + relativedelta(months=-6))])
        daily_sales_ids = self.env['sale.order'].search([('state', '=', 'sale')]).ids
        daily_sales_line = self.env['sale.order.line'].search([('order_id', 'in', daily_sales_ids)])
        total_sales = self.env['sale.order'].search_count([('state', '=', 'sale')])

        ## Total sales by month
        total_sales_by_month = {}
        first_month = datetime.now().month - 5
        if first_month < 1:
            first_month = 12 + first_month

        for x in range(first_month, first_month+6):
            month = x
            if month > 12:
                month = x - 12
            total_sales_by_month[month] = {'month': calendar.month_name[month], 'total': 0}

        for sales in daily_sales:
            if sales.flsp_so_date:
                current_month = sales.flsp_so_date.month
            print('current_month: '+str(current_month)+' - total: '+str(sales.amount_total))
            if current_month in total_sales_by_month:
                total_sales_by_month[current_month]['total'] += sales.amount_total

        print(total_sales_by_month)
        for x in total_sales_by_month:
            print(calendar.month_name[x])


        # name plus an array of sales by product category + graph style top and bottom:
        # { 1: {'name': 'Sam',  'SBS':0, 'PPE': 6000, 'SA': 0, 'stSBS':0, 'stPPE': 0, 'stSA': 0
        #                                                    , 'sbSBS':0, 'sbPPE': 0, 'sbSA': 0},
        sale_by_person = {}

        for sale in daily_sales:
            key = len(sale_by_person) + 1
            for x in sale_by_person:
                if sale_by_person[x]['name'] == sale.user_id.name:
                    key = x

            order_lines = self.env['sale.order.line'].search([('order_id', '=', sale.id)])
            ppe_value = 0
            sbs_value = 0
            sa_value  = 0
            top_val = 0
            for line in order_lines:
                if line.product_id.categ_id.name == 'School PPE Program':
                    ppe_value += line.price_total
                if line.product_id.categ_id.name == 'School Bus Signs':
                    sbs_value += line.price_total
                if line.product_id.categ_id.name == 'Stop Arms':
                    sa_value += line.price_total

            if key > len(sale_by_person):
                sale_by_person[key] = {'name': sale.user_id.name, 'SBS': sbs_value, 'PPE': ppe_value, 'SA': sa_value,
                                       'stSBS':0, 'stPPE': 6000, 'stSA': 0, 'sbSBS':0, 'sbPPE': 6000, 'sbSA': 0, }
            else:
                sale_by_person[key]['SBS'] += sbs_value
                sale_by_person[key]['PPE'] += ppe_value
                sale_by_person[key]['SA']  += sa_value

        # Style for the graph
        for x in sale_by_person:
            if top_val < sale_by_person[x]['SBS']:
                top_val = sale_by_person[x]['SBS']
            if top_val < sale_by_person[x]['PPE']:
                top_val = sale_by_person[x]['PPE']
            if top_val < sale_by_person[x]['SA']:
                top_val = sale_by_person[x]['SA']

        for x in sale_by_person:
            sale_by_person[x]['sbSBS'] = ((sale_by_person[x]['SBS']*100)//top_val)*2
            sale_by_person[x]['sbPPE'] = ((sale_by_person[x]['PPE']*100)//top_val)*2
            sale_by_person[x]['sbSA'] = ((sale_by_person[x]['SA']*100)//top_val)*2
            sale_by_person[x]['stSBS'] = 200-sale_by_person[x]['sbSBS']
            sale_by_person[x]['stPPE'] = 200-sale_by_person[x]['sbPPE']
            sale_by_person[x]['stSA'] = 200-sale_by_person[x]['sbSA']

        print('top_val:')
        print(top_val)
        for x in sale_by_person:
            print(sale_by_person[x])
        print('rendered_body')
        rendered_body = template.render({'total_sales_by_month': total_sales_by_month,
                                         'sale_by_person': sale_by_person, }, engine='ir.qweb')
        body = self.env['mail.thread']._replace_local_links(rendered_body)

        print('Sending email')
        self.env['mail.mail'].create({
            'body_html': body,
            'subject': 'Weekly Sales Order Report',
            'email_to': 'alexandresousa@smartrendmfg.com',
            'auto_delete': True,
        }).send()

        ## Check the sent sales Order
        print('Check the sent sales Order')
        for so in daily_sales:
            so.flsp_email_report_ok = True

        print('************ weekly Sales Order Report - DONE ******************')
