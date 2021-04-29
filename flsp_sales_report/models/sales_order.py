# -*- coding: utf-8 -*-
import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class SalesOrderReport(models.Model):
    _inherit = "sale.order"
    _check_company_auto = True

    flsp_utm_other_source = fields.Char(string="Other Source Desc.")
    flsp_source_name = fields.Char(string="Other Source")

    @api.onchange('source_id')
    def _onchange_source_id(self):
        self.flsp_source_name = self.source_id.name


    def weekly_email_report(self):
        data = {}
        data['qty'] = {}
        data['val'] = {}

        qty_values = self.calc_sales_qty_val()
        dollar_val = self.calc_sales_dollar_val()

        total_categs = 0

        data['qty']['categ'] = {}
        data['val']['categ'] = {}
        product_categories = self.env['product.category'].search([('flsp_weekly_report', '=', True)])
        for product_cateory in product_categories:
            total_categs += 1
            data['qty']['categ'][product_cateory.id] = []
            data['qty']['categ'][product_cateory.id].append(product_cateory.flsp_name_report)
            data['qty']['categ'][product_cateory.id].append(product_cateory.flsp_report_color)
            data['val']['categ'][product_cateory.id] = []
            data['val']['categ'][product_cateory.id].append(product_cateory.flsp_name_report)
            data['val']['categ'][product_cateory.id].append(product_cateory.flsp_report_color)

        data['qty']['months'] = {}
        data['val']['months'] = {}
        current_date = date.today()
        current_year = current_date.year
        current_month = current_date.month
        first_month = current_month - 2
        if first_month < 0:
            first_month += 12
        second_month = current_month - 1
        if second_month < 0:
            second_month += 12
        data['qty']['months'][first_month] = calendar.month_name[first_month]
        data['qty']['months'][second_month] = calendar.month_name[second_month]
        data['qty']['months'][current_month] = calendar.month_name[current_month]
        data['val']['months'][first_month] = calendar.month_name[first_month]
        data['val']['months'][second_month] = calendar.month_name[second_month]
        data['val']['months'][current_month] = calendar.month_name[current_month]


        data['qty']['salesteam'] = {}
        data['val']['salesteam'] = {}
        sales_teams = self.env['crm.team'].search([])
        for sales_team in sales_teams:
            if sales_team.flsp_weekly_report:
                data['qty']['salesteam'][sales_team.id] = sales_team
                data['val']['salesteam'][sales_team.id] = sales_team

        ###################################################################
        # Quantity                                                        #
        ###################################################################
        # Header:  Team     YTD     January        February         March
        tr_count = 1
        data['qty']['tr'] = {}
        data['qty']['tr'][tr_count] = []

        data['qty']['tr'][tr_count].append('<td  class="column_header">Team</td>')
        data['qty']['tr'][tr_count].append('<td colspan="'+str(total_categs*2)+'" class="column_header">YTD</td>')
        for key in data['qty']['months']:
            data['qty']['tr'][tr_count].append('<td colspan="'+str(total_categs*2)+'" class="column_header">'+data['qty']['months'][key]+'</td>')

        # Header:  Team     FISA   FISA%   SSA   SSA%     ISBS      ISBS%
        tr_count += 1
        data['qty']['tr'][tr_count] = []
        data['qty']['tr'][tr_count].append('<td class="data_td team_td"> </td>')
        for category in data['qty']['categ']:
            data['qty']['tr'][tr_count].append('<td class="categ_td" bgcolor="'+data['qty']['categ'][category][1]+'" > '+data['qty']['categ'][category][0]+' </td>')
            data['qty']['tr'][tr_count].append('<td class="categ_td" bgcolor="' + data['qty']['categ'][category][1] + '" > ' + data['qty']['categ'][category][0] + '%</td>')
        for key in data['qty']['months']:
            for category in data['qty']['categ']:
                data['qty']['tr'][tr_count].append('<td class="categ_td" bgcolor="' + data['qty']['categ'][category][1] + '" > ' + data['qty']['categ'][category][0] + ' </td>')
                data['qty']['tr'][tr_count].append('<td class="categ_td" bgcolor="' + data['qty']['categ'][category][1] + '" > ' + data['qty']['categ'][category][0] + '%</td>')
            # print(data['qty']['categ'][category][0])  # categ
            # print(data['qty']['categ'][category][1])  # color

        # Data:  Sales Team and Values
        for team in data['qty']['salesteam']:
            tr_count += 1
            data['qty']['tr'][tr_count] = []
            data['qty']['tr'][tr_count].append('<td class="data_td team_td">'+data['qty']['salesteam'][team].name+'</td>')
            for category in data['qty']['categ']:
                # data['qty']['tr'][tr_count].append('<td class="total_data_td" bgcolor="' + data['qty']['categ'][category][1] + '" >'+qty_values[team][0][category][0]+'</td>')
                # data['qty']['tr'][tr_count].append('<td class="total_data_td" bgcolor="' + data['qty']['categ'][category][1] + '" >'+qty_values[team][0][category][1]+'</td>')
                if qty_values[team][0][category][3]:
                    data['qty']['tr'][tr_count].append('<td class="total_data_td" bgcolor="#00B050" >'+qty_values[team][0][category][0]+'</td>')
                    data['qty']['tr'][tr_count].append('<td class="total_data_td" bgcolor="#00B050" >'+qty_values[team][0][category][1]+'</td>')
                else:
                    data['qty']['tr'][tr_count].append('<td class="total_data_td" >'+qty_values[team][0][category][0]+'</td>')
                    data['qty']['tr'][tr_count].append('<td class="total_data_td" >'+qty_values[team][0][category][1]+'</td>')
            for key in data['qty']['months']:
                for category in data['qty']['categ']:
                    if qty_values[team][key][category][3]:
                        data['qty']['tr'][tr_count].append('<td class="total_data_td" bgcolor="#00B050">'+qty_values[team][key][category][0]+'</td>')
                        data['qty']['tr'][tr_count].append('<td class="total_data_td" bgcolor="#00B050">'+qty_values[team][key][category][1]+'</td>')
                    else:
                        data['qty']['tr'][tr_count].append('<td class="total_data_td">'+qty_values[team][key][category][0]+'</td>')
                        data['qty']['tr'][tr_count].append('<td class="total_data_td">'+qty_values[team][key][category][1]+'</td>')

        # **************** Total:
        tr_count += 1
        data['qty']['tr'][tr_count] = []
        data['qty']['tr'][tr_count].append('<td class="total_row_td team_td">Total</td>')
        # Year to date
        for category in data['qty']['categ']:
            # data['qty']['tr'][tr_count].append('<td class="total_row_td" bgcolor="' + data['qty']['categ'][category][1] + '" >'+qty_values[0][0][category][0]+'</td>')
            # data['qty']['tr'][tr_count].append('<td class="total_row_td" bgcolor="' + data['qty']['categ'][category][1] + '" >'+qty_values[0][0][category][1]+'</td>')
            data['qty']['tr'][tr_count].append('<td class="total_row_td">'+qty_values[0][0][category][0]+'</td>')
            data['qty']['tr'][tr_count].append('<td class="total_row_td">'+qty_values[0][0][category][1]+'</td>')
        # 3 previous months
        for key in data['qty']['months']:
            for category in data['qty']['categ']:
                # data['qty']['tr'][tr_count].append('<td class="total_row_td" bgcolor="'+data['qty']['categ'][category][1]+'" >'+qty_values[0][key][category][0]+'</td>')
                # data['qty']['tr'][tr_count].append('<td class="total_row_td" bgcolor="'+data['qty']['categ'][category][1]+'" >'+qty_values[0][key][category][1]+'</td>')
                data['qty']['tr'][tr_count].append('<td class="total_row_td">'+qty_values[0][key][category][0]+'</td>')
                data['qty']['tr'][tr_count].append('<td class="total_row_td">'+qty_values[0][key][category][1]+'</td>')

        # **************** Target:
        tr_count += 1
        data['qty']['tr'][tr_count] = []
        data['qty']['tr'][tr_count].append('<td class="data_td team_td">Target</td>')
        # Year to date
        for category in data['qty']['categ']:
            # data['qty']['tr'][tr_count].append('<td class="data_td" bgcolor="' + data['qty']['categ'][category][1] + '" >'+qty_values[9999][0][category][0]+'</td>')
            # data['qty']['tr'][tr_count].append('<td class="data_td" bgcolor="' + data['qty']['categ'][category][1] + '" ></td>')
            data['qty']['tr'][tr_count].append('<td class="data_td">'+qty_values[9999][0][category][0]+'</td>')
            data['qty']['tr'][tr_count].append('<td class="data_td"></td>')
        # 3 previous months
        for key in data['qty']['months']:
            for category in data['qty']['categ']:
                # data['qty']['tr'][tr_count].append('<td class="data_td" bgcolor="'+data['qty']['categ'][category][1]+'" >'+qty_values[9999][key][category][0]+'</td>')
                # data['qty']['tr'][tr_count].append('<td class="data_td" bgcolor="'+data['qty']['categ'][category][1]+'" ></td>')
                data['qty']['tr'][tr_count].append('<td class="data_td">'+qty_values[9999][key][category][0]+'</td>')
                data['qty']['tr'][tr_count].append('<td class="data_td"></td>')

        ###################################################################
        # Dollar                                                          #
        ###################################################################
        # Header:  Team     YTD     January        February         March
        tr_count = 1
        data['val']['tr'] = {}
        data['val']['tr'][tr_count] = []

        data['val']['tr'][tr_count].append('<td  class="column_header">Team</td>')
        data['val']['tr'][tr_count].append('<td colspan="'+str(total_categs*2)+'" class="column_header">YTD</td>')
        for key in data['val']['months']:
            data['val']['tr'][tr_count].append('<td colspan="'+str(total_categs*2)+'" class="column_header">'+data['val']['months'][key]+'</td>')

        # Header:  Team     FISA   FISA%   SSA   SSA%     ISBS      ISBS%
        tr_count += 1
        data['val']['tr'][tr_count] = []
        data['val']['tr'][tr_count].append('<td class="data_td team_td"> </td>')
        for category in data['val']['categ']:
            data['val']['tr'][tr_count].append('<td class="categ_td" bgcolor="'+data['val']['categ'][category][1]+'" > '+data['val']['categ'][category][0]+' </td>')
            data['val']['tr'][tr_count].append('<td class="categ_td" bgcolor="' + data['val']['categ'][category][1] + '" > ' + data['val']['categ'][category][0] + '%</td>')
        for key in data['val']['months']:
            for category in data['val']['categ']:
                data['val']['tr'][tr_count].append('<td class="categ_td" bgcolor="' + data['val']['categ'][category][1] + '" > ' + data['val']['categ'][category][0] + ' </td>')
                data['val']['tr'][tr_count].append('<td class="categ_td" bgcolor="' + data['val']['categ'][category][1] + '" > ' + data['val']['categ'][category][0] + '%</td>')
            # print(data['val']['categ'][category][0])  # categ
            # print(data['val']['categ'][category][1])  # color

        # Data:  Sales Team and Values
        for team in data['val']['salesteam']:
            tr_count += 1
            data['val']['tr'][tr_count] = []
            data['val']['tr'][tr_count].append('<td class="data_td team_td">'+data['val']['salesteam'][team].name+'</td>')
            for category in data['val']['categ']:
                if dollar_val[team][0][category][3]:
                    data['val']['tr'][tr_count].append('<td class="total_data_td" bgcolor="#00B050">'+dollar_val[team][0][category][0]+'</td>')
                    data['val']['tr'][tr_count].append('<td class="total_data_td" bgcolor="#00B050">'+dollar_val[team][0][category][1]+'</td>')
                else:
                    data['val']['tr'][tr_count].append('<td class="total_data_td">'+dollar_val[team][0][category][0]+'</td>')
                    data['val']['tr'][tr_count].append('<td class="total_data_td">'+dollar_val[team][0][category][1]+'</td>')
            for key in data['val']['months']:
                for category in data['val']['categ']:
                    if dollar_val[team][key][category][3]:
                        data['val']['tr'][tr_count].append('<td class="total_data_td" bgcolor="#00B050">'+dollar_val[team][key][category][0]+'</td>')
                        data['val']['tr'][tr_count].append('<td class="total_data_td" bgcolor="#00B050">'+dollar_val[team][key][category][1]+'</td>')
                    else:
                        data['val']['tr'][tr_count].append('<td class="total_data_td">'+dollar_val[team][key][category][0]+'</td>')
                        data['val']['tr'][tr_count].append('<td class="total_data_td">'+dollar_val[team][key][category][1]+'</td>')
        # **************** Total:
        tr_count += 1
        data['val']['tr'][tr_count] = []
        data['val']['tr'][tr_count].append('<td class="total_row_td team_td">Total</td>')
        # Year to date
        for category in data['val']['categ']:
            # data['val']['tr'][tr_count].append('<td class="total_row_td" bgcolor="' + data['val']['categ'][category][1] + '" >'+dollar_val[0][0][category][0]+'</td>')
            # data['val']['tr'][tr_count].append('<td class="total_row_td" bgcolor="' + data['val']['categ'][category][1] + '" >'+dollar_val[0][0][category][1]+'</td>')
            data['val']['tr'][tr_count].append('<td class="total_row_td">'+dollar_val[0][0][category][0]+'</td>')
            data['val']['tr'][tr_count].append('<td class="total_row_td">'+dollar_val[0][0][category][1]+'</td>')
        # 3 previous months
        for key in data['val']['months']:
            for category in data['val']['categ']:
                # data['val']['tr'][tr_count].append('<td class="total_row_td" bgcolor="'+data['val']['categ'][category][1]+'" >'+dollar_val[0][key][category][0]+'</td>')
                # data['val']['tr'][tr_count].append('<td class="total_row_td" bgcolor="'+data['val']['categ'][category][1]+'" >'+dollar_val[0][key][category][1]+'</td>')
                data['val']['tr'][tr_count].append('<td class="total_row_td">'+dollar_val[0][key][category][0]+'</td>')
                data['val']['tr'][tr_count].append('<td class="total_row_td">'+dollar_val[0][key][category][1]+'</td>')

        return data

    def calc_sales_qty_val(self):
        a_ret = {}
        #####################################################################
        #    Creating structure of array a_ret:
        #    a_ret[TEAM_ID][MONTH][CATEG] = {QTY_STR, %, NUMERIC, IsHighest}
        #    a_ret[TEAM_ID][MONTH][TOTAL=0] = {QTY_STR, %, NUMERIC, IsHighest}
        #    a_ret[TEAM_ID][YTD=0][CATEG] = {QTY_STR, %, NUMERIC, IsHighest}
        #    a_ret[TEAM_ID][YTD=0][TOTAL=0] = {QTY_STR, %, NUMERIC, IsHighest}
        #    a_ret[Target=9999][MONTH][CATEG] = {QTY_STR, %, NUMERIC, IsHighest}
        #####################################################################
        sales_teams = self.env['crm.team'].search([])
        for sales_team in sales_teams:
            if sales_team.flsp_weekly_report:
                a_ret[sales_team.id] = {}
                for i in range(0, 13):
                    a_ret[sales_team.id][i] = {}
                    product_categories = self.env['product.category'].search([('flsp_weekly_report', '=', True)])
                    a_ret[sales_team.id][i][0] = ['0', '0%', 0, False]
                    for product_cateory in product_categories:
                        a_ret[sales_team.id][i][product_cateory.id] = ['0','0%', 0, False]
        for x in range(0, 2):
            key = 0 if x == 0 else 9999
            a_ret[key] = {}
            for i in range(0, 13):
                a_ret[key][i] = {}
                product_categories = self.env['product.category'].search([('flsp_weekly_report', '=', True)])
                a_ret[key][i][0] = ['0', '0%', 0, False]
                for product_cateory in product_categories:
                        a_ret[key][i][product_cateory.id] = ['0', '0%', 0, False]
        ##################################################
        # Filling out array with data                    #
        ##################################################
        date_start = datetime.strptime('01/01/'+str(date.today().year)+' 00:00:00', '%d/%m/%Y %H:%M:%S')
        date_end = datetime.strptime('31/12/'+str(date.today().year)+' 23:59:59', '%d/%m/%Y %H:%M:%S')
        sales_orders = self.env['sale.order'].search(['&', ('state', 'in', ['sale', 'done']), '&', ('date_order','>=', date_start), ('date_order','<=', date_end)])
        for so in sales_orders:
            if so.amount_total <= 1:
                sales_order_lines = self.env['sale.order.line'].search([('order_id', '=', so.id)])
                for sol in sales_order_lines:
                    if sol.product_id.categ_id.flsp_weekly_report and so.team_id.flsp_weekly_report:
                        qty = 0
                        if 'DEMO' in sol.product_id.name:
                            if so.state == 'sale':
                                qty = sol.product_uom_qty / 2
                            else:
                                # case the SO is marked as done without delivering some products
                                qty = sol.qty_delivered / 2
                            a_ret[so.team_id.id][so.date_order.month][sol.product_id.categ_id.id][2] += qty
                            a_ret[so.team_id.id][0][sol.product_id.categ_id.id][2] += qty
                            a_ret[0][so.date_order.month][sol.product_id.categ_id.id][2] += qty
                            a_ret[0][0][sol.product_id.categ_id.id][2] += qty
                continue
            sales_order_lines = self.env['sale.order.line'].search([('order_id', '=', so.id)])
            for sol in sales_order_lines:
                if sol.product_id.categ_id.flsp_weekly_report and so.team_id.flsp_weekly_report:
                    qty = 0
                    if so.state == 'sale':
                        qty = sol.product_uom_qty
                    else:
                        # case the SO is marked as done without delivering some products
                        qty = sol.qty_delivered
                    if 'SET,' in sol.product_id.name:
                        # Duplicate in case of SET
                        qty = qty * 2

                    a_ret[so.team_id.id][so.date_order.month][sol.product_id.categ_id.id][2] += qty
                    a_ret[so.team_id.id][0][sol.product_id.categ_id.id][2] += qty
                    a_ret[0][so.date_order.month][sol.product_id.categ_id.id][2] += qty
                    a_ret[0][0][sol.product_id.categ_id.id][2] += qty

        ##################################################
        # Target by Category                             #
        ##################################################
        categories = self.env['product.category'].search([('flsp_weekly_report', '=', True)])
        for categ in categories:
            target = self.env['flsp.sale.target.category'].search(['&', ('category_id', '=', categ.id), ('year', '=', str(date.today().year))], limit=1)
            for month in a_ret[9999]:
                if month == 0:
                    continue
                a_ret[9999][month][categ.id][2] = target['month'+str(month).zfill(2)]
                a_ret[9999][0][categ.id][2] += target['month' + str(month).zfill(2)]
        ##################################################
        # Organizing % of totals into the array          #
        ##################################################
        for team in a_ret:
            for month in a_ret[team]:
                for categ in a_ret[team][month]:
                    # TODO: format here
                    a_ret[team][month][categ][0] = str(a_ret[team][month][categ][2])
                    if a_ret[0][month][categ][2] > 0:
                        a_ret[team][month][categ][1] = "{:0.0f}".format(a_ret[team][month][categ][2]/a_ret[0][month][categ][2]*100)+'%'
                    if a_ret[9999][month][categ][2] > 0:
                        a_ret[0][month][categ][1] = "{:0.0f}".format(a_ret[0][month][categ][2]/a_ret[9999][month][categ][2]*100)+'%'

        ##################################################
        # Highlighting the leader                        #
        ##################################################
        for lead_month in range(0, 13):
            product_categories = self.env['product.category'].search([('flsp_weekly_report', '=', True)])
            for product_cateory in product_categories:
                lead_categ = product_cateory.id
                lead_team = 0
                lead_value = 0
                for team in a_ret:
                    if team > 0 and team < 9999:
                        for month in a_ret[team]:
                            if month == lead_month:
                                for categ in a_ret[team][month]:
                                    if categ == lead_categ:
                                        if lead_value < a_ret[team][month][categ][2]:
                                            lead_value = a_ret[team][month][categ][2]
                                            lead_team = team
                a_ret[lead_team][lead_month][lead_categ][3] = True

        return a_ret

    def calc_sales_dollar_val(self):
        us_currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id
        a_ret = {}
        #####################################################################
        #    Creating structure of array a_ret:
        #    a_ret[TEAM_ID][MONTH][CATEG] = {QTY_STR, %, NUMERIC, IsHighest}
        #    a_ret[TEAM_ID][MONTH][TOTAL=0] = {QTY_STR, %, NUMERIC, IsHighest}
        #    a_ret[TEAM_ID][YTD=0][CATEG] = {QTY_STR, %, NUMERIC, IsHighest}
        #    a_ret[TEAM_ID][YTD=0][TOTAL=0] = {QTY_STR, %, NUMERIC, IsHighest}
        #    a_ret[Target=9999][MONTH][CATEG] = {QTY_STR, %, NUMERIC, IsHighest}
        #####################################################################
        sales_teams = self.env['crm.team'].search([])
        for sales_team in sales_teams:
            if sales_team.flsp_weekly_report:
                a_ret[sales_team.id] = {}
                for i in range(0, 13):
                    a_ret[sales_team.id][i] = {}
                    product_categories = self.env['product.category'].search([('flsp_weekly_report', '=', True)])
                    a_ret[sales_team.id][i][0] = ['0', '0%', 0, False]
                    for product_cateory in product_categories:
                        a_ret[sales_team.id][i][product_cateory.id] = ['0','0%', 0, False]
        for x in range(0, 2):
            key = 0 if x == 0 else 9999
            a_ret[key] = {}
            for i in range(0, 13):
                a_ret[key][i] = {}
                product_categories = self.env['product.category'].search([('flsp_weekly_report', '=', True)])
                a_ret[key][i][0] = ['0', '0%', 0, False]
                for product_cateory in product_categories:
                        a_ret[key][i][product_cateory.id] = ['0', '0%', 0, False]
        ##################################################
        # Filling out array with data                    #
        ##################################################
        date_start = datetime.strptime('01/01/'+str(date.today().year)+' 00:00:00', '%d/%m/%Y %H:%M:%S')
        date_end = datetime.strptime('31/12/'+str(date.today().year)+' 23:59:59', '%d/%m/%Y %H:%M:%S')
        sales_orders = self.env['sale.order'].search(['&', ('state', 'in', ['sale', 'done']), '&', ('date_order','>=', date_start), ('date_order','<=', date_end)])
        for so in sales_orders:
            if so.amount_total <= 1:
                sales_order_lines = self.env['sale.order.line'].search([('order_id', '=', so.id)])
                for sol in sales_order_lines:
                    if sol.product_id.categ_id.flsp_weekly_report and so.team_id.flsp_weekly_report:
                        dollar_val = 0
                        if sol.currency_id.name == 'USD':
                            dollar_val = sol.price_unit
                        elif sol.currency_id.name == 'CAD':
                            usd_rate = self.env['res.currency.rate'].search([('currency_id', '=', us_currency_id)],
                                                                            limit=1)
                            dollar_val = sol.price_unit * usd_rate.rate
                        qty = 0
                        if 'DEMO' in sol.product_id.name:
                            if so.state == 'sale':
                                qty = sol.product_uom_qty * dollar_val
                            else:
                                # case the SO is marked as done without delivering some products
                                qty = sol.qty_delivered * dollar_val
                            a_ret[so.team_id.id][so.date_order.month][sol.product_id.categ_id.id][2] += qty
                            a_ret[so.team_id.id][0][sol.product_id.categ_id.id][2] += qty
                            a_ret[0][so.date_order.month][sol.product_id.categ_id.id][2] += qty
                            a_ret[0][0][sol.product_id.categ_id.id][2] += qty
                continue
            sales_order_lines = self.env['sale.order.line'].search([('order_id', '=', so.id)])
            for sol in sales_order_lines:
                if sol.product_id.categ_id.flsp_weekly_report and so.team_id.flsp_weekly_report:
                    dollar_val = 0
                    if sol.currency_id.name == 'USD':
                        dollar_val = sol.price_unit
                    elif sol.currency_id.name == 'CAD':
                        usd_rate = self.env['res.currency.rate'].search([('currency_id', '=', us_currency_id)], limit=1)
                        dollar_val = sol.price_unit*usd_rate.rate
                    qty = 0
                    if so.state == 'sale':
                        qty = sol.product_uom_qty*dollar_val
                    else:
                        # case the SO is marked as done without delivering some products
                        qty = sol.qty_delivered*dollar_val
                    # if 'SET,' in sol.product_id.name:
                        # Duplicate in case of SET
                        # qty = qty * 2
                    # if 'DEMO' in sol.product_id.name:
                        # To consider half in case of Demo
                        # qty = qty / 2

                    a_ret[so.team_id.id][so.date_order.month][sol.product_id.categ_id.id][2] += qty
                    a_ret[so.team_id.id][0][sol.product_id.categ_id.id][2] += qty
                    a_ret[0][so.date_order.month][sol.product_id.categ_id.id][2] += qty
                    a_ret[0][0][sol.product_id.categ_id.id][2] += qty
        ##################################################
        # Target by Category                             #
        ##################################################
        categories = self.env['product.category'].search([('flsp_weekly_report', '=', True)])
        for categ in categories:
            target = self.env['flsp.sale.target.category'].search(['&', ('category_id', '=', categ.id), ('year', '=', str(date.today().year))], limit=1)
            for month in a_ret[9999]:
                if month == 0:
                    continue
                a_ret[9999][month][categ.id][2] = target['month'+str(month).zfill(2)]
                a_ret[9999][0][categ.id][2] += target['month' + str(month).zfill(2)]
        ##################################################
        # Organizing % of totals into the array          #
        ##################################################
        for team in a_ret:
            for month in a_ret[team]:
                for categ in a_ret[team][month]:
                    # TODO: format here
                    a_ret[team][month][categ][0] = "{:,.0f}".format(a_ret[team][month][categ][2])
                    if a_ret[0][month][categ][2] > 0:
                        a_ret[team][month][categ][1] = "{:0.0f}".format(a_ret[team][month][categ][2]/a_ret[0][month][categ][2]*100)+'%'
                    if a_ret[9999][month][categ][2] > 0:
                        a_ret[0][month][categ][1] = " "
        ##################################################
        # Highlighting the leader                        #
        ##################################################
        for lead_month in range(0, 13):
            product_categories = self.env['product.category'].search([('flsp_weekly_report', '=', True)])
            for product_cateory in product_categories:
                lead_categ = product_cateory.id
                lead_team = 0
                lead_value = 0
                for team in a_ret:
                    if team > 0 and team < 9999:
                        for month in a_ret[team]:
                            if month == lead_month:
                                for categ in a_ret[team][month]:
                                    if categ == lead_categ:
                                        if lead_value < a_ret[team][month][categ][2]:
                                            lead_value = a_ret[team][month][categ][2]
                                            lead_team = team
                a_ret[lead_team][lead_month][lead_categ][3] = True

        return a_ret
