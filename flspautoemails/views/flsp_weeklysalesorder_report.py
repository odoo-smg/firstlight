# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import api, models


class ReportSalesbysalesperson(models.AbstractModel):
    _name = 'report.flspautoemails.flsp_rep_weeklysalesorder'
    _description = 'Weekly Sales by Salesperson'

    @api.model
    def _get_report_values(self, docids, data=None):

        d_from = date.today() + relativedelta(days=-7)
        d_to = date.today()

        us_currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id
        daily_sales = self.env['sale.order'].search(['&',
                                                     ('state', 'in', ['sale', 'done']),
                                                     ('date_order', '>', date.today() + relativedelta(months=-6))])

        ## Total sales by month
        total_sales_by_month = {0: {'month': 'Category', 'total': 0, 'category': {0: {'categ': 'Total', 'total': 0}}}}
        first_month = datetime.now().month - 5
        if first_month < 1:
            first_month = 12 + first_month

        for x in range(first_month, first_month+6):
            month = x
            if month > 12:
                month = x - 12
            total_sales_by_month[month] = {'month': calendar.month_name[month], 'total': 0, 'category': {}}

        for sales in daily_sales:
            if sales.date_order:
                current_month = sales.date_order.month
            if current_month in total_sales_by_month:
                if sales.currency_id.name == 'USD':
                    total_sales_by_month[current_month]['total'] += sales.amount_total
                elif sales.currency_id.name == 'CAD':
                    usd_rate = self.env['res.currency.rate'].search([('currency_id', '=', us_currency_id)], limit=1)
                    total_sales_by_month[current_month]['total'] += (float(sales.amount_total) * float(usd_rate.rate))

                order_lines = self.env['sale.order.line'].search([('order_id', '=', sales.id)])
                for line in order_lines:
                    categ_val = 0
                    if line.currency_id.name == 'USD':
                        categ_val = line.price_total
                    elif line.currency_id.name == 'CAD':
                        usd_rate = self.env['res.currency.rate'].search([('currency_id', '=', us_currency_id)], limit=1)
                        categ_val = line.price_total*usd_rate.rate

                    if categ_val > 0:
                        if line.product_id.categ_id.id in total_sales_by_month[current_month]['category']:
                            total_sales_by_month[current_month]['category'][line.product_id.categ_id.id]['total'] = total_sales_by_month[current_month]['category'][line.product_id.categ_id.id]['total']+categ_val
                        else:
                            total_sales_by_month[current_month]['category'][line.product_id.categ_id.id] = {'categ': line.product_id.categ_id.name, 'total': categ_val}
        for month in total_sales_by_month:
            for categ_id in total_sales_by_month[month]['category']:
                if not(categ_id in total_sales_by_month[0]['category']):
                    total_sales_by_month[0]['category'][categ_id] = total_sales_by_month[month]['category'][categ_id]

        # name plus an array of sales by product category + graph style top and bottom:
        # { 1: {'name': 'Sam',  'SBS':0, 'PPE': 6000, 'SA': 0, 'stSBS':0, 'stPPE': 0, 'stSA': 0
        #                                                    , 'sbSBS':0, 'sbPPE': 0, 'sbSA': 0},
        sale_by_person = {}
        top_val = 0
        daily_sales = self.env['sale.order'].search(['&',
                                                     ('state', 'in', ['sale', 'done']),
                                                     ('date_order', '>', date.today() + relativedelta(days=-7))])
        for sale in daily_sales:
            key = len(sale_by_person) + 1
            for x in sale_by_person:
                if sale_by_person[x]['name'] == sale.user_id.name:
                    key = x

            order_lines = self.env['sale.order.line'].search([('order_id', '=', sale.id)])
            ppe_value = 0
            sbs_value = 0
            sa_value  = 0
            for line in order_lines:
                current_total = 0
                if line.currency_id.name == 'USD':
                    current_total = line.price_total
                elif line.currency_id.name == 'CAD':
                    usd_rate = self.env['res.currency.rate'].search([('currency_id', '=', us_currency_id)], limit=1)
                    current_total = (float(line.price_total) * float(usd_rate.rate))

                if line.product_id.categ_id.name == 'School PPE Program':
                    ppe_value += current_total
                if line.product_id.categ_id.name == 'School Bus Signs':
                    sbs_value += current_total
                if line.product_id.categ_id.name == 'Stop Arms':
                    sa_value += current_total

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

        # add 5% to make the report more readable / avoid zero division
        if top_val == 0:
            top_val = 1
        else:
            top_val += (top_val*5/100)

        for x in sale_by_person:
            sale_by_person[x]['sbSBS'] = ((sale_by_person[x]['SBS']*100)//top_val)*2
            sale_by_person[x]['sbPPE'] = ((sale_by_person[x]['PPE']*100)//top_val)*2
            sale_by_person[x]['sbSA'] = ((sale_by_person[x]['SA']*100)//top_val)*2
            sale_by_person[x]['stSBS'] = 200-sale_by_person[x]['sbSBS']
            sale_by_person[x]['stPPE'] = 200-sale_by_person[x]['sbPPE']
            sale_by_person[x]['stSA'] = 200-sale_by_person[x]['sbSA']

        return {
            'total_sales_by_month' : total_sales_by_month,
            'sale_by_person' : sale_by_person,
            'd_from' : d_from,
            'd_to' : d_to,
        }
