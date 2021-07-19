# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
from lxml import etree
from dateutil.relativedelta import relativedelta

class FlspSalesForecast(models.Model):
    """
            Class_Name: FlspSalesForecast
            Model_Name: flsp_sales_forecast
            Purpose:    To help create the flsp_sales_forecast
            Date:       Dec/15th/2020/W
            Updated:
            Author:     Sami Byaruhanga
    """

    _name = 'flsp.sales.forecast'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Flsp Sales Forecast'
    _rec_name = "product_id"

    _sql_constraints = [
        ('default_product_unique',
         'UNIQUE(product_id)',
         "A forecast for this product already exists.\n"
         "Delete this record, return to tree view and search for product of choice.Edit to add the forecast info"),
    ]
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    product_id = fields.Many2one('product.product', string='Product',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, tracking=True)

    # User table to fill
    forecast_line = fields.One2many('flsp.sales.forecast.line', 'order_id', string='Order Lines', copy=True, nauto_join=True)

    # Note: only need to call compute in 1 function. it depends on other fields and updating the qty any ways
    qty_month1 = fields.Float(string='January', compute='_qty_based_off_date', store=True)
    qty_month2 = fields.Float(string='February')
    qty_month3 = fields.Float(string='March')
    qty_month4 = fields.Float(string='April')
    qty_month5 = fields.Float(string='May')
    qty_month6 = fields.Float(string='June')
    qty_month7 = fields.Float(string='July')
    qty_month8 = fields.Float(string='August')
    qty_month9 = fields.Float(string='September')
    qty_month10 = fields.Float(string='October')
    qty_month11 = fields.Float(string='November')
    qty_month12 = fields.Float(string='December')

    # (line.date_planned.strftime('%B')) gives the month name
    # (line.date_planned.month gives the month number
    @api.depends('forecast_line.forecast_qty', 'forecast_line.forecast_date')
    def _qty_based_off_date(self):
        """
            Purpose: To calculate monthly quantities
        """
        for order in self:
            qty1 =0.0
            qty2 =0.0
            qty3 =0.0
            qty4 =0.0
            qty5 =0.0
            qty6 =0.0
            qty7 =0.0
            qty8 =0.0
            qty9 =0.0
            qty10 =0.0
            qty11 =0.0
            qty12 =0.0
            for line in order.forecast_line:
                forecast = line.forecast_date
                # this_year = datetime.today().year #2020
                # nxt_year = datetime.today().year + 1 #2021
                if forecast:
                    if ((forecast.year > datetime.today().year + 1) or (forecast.year == datetime.today().year + 1 and forecast.month >= datetime.today().month)):
                        continue
                    if (forecast.year < datetime.today().year or (forecast.year == datetime.today().year and forecast.month < datetime.today().month)):
                        continue

                    if forecast.month == 1:
                        # if forecast.year < this_year:
                        #     qty1 =0
                        #     print("zero for last year value")
                        # else:
                        qty1 += line.forecast_qty
                    elif forecast.month == 2:
                        qty2 += line.forecast_qty
                    elif forecast.month == 3:
                        qty3 += line.forecast_qty
                    elif forecast.month == 4:
                        qty4 += line.forecast_qty
                    elif forecast.month == 5:
                        qty5 += line.forecast_qty
                    elif forecast.month == 6:
                        qty6 += line.forecast_qty
                    elif forecast.month == 7:
                        qty7 += line.forecast_qty
                    elif forecast.month == 8:
                        qty8 += line.forecast_qty
                    elif forecast.month == 9:
                        qty9 += line.forecast_qty
                    elif forecast.month == 10:
                        qty10 += line.forecast_qty
                    elif forecast.month == 11:
                        qty11 += line.forecast_qty
                    elif forecast.month == 12:
                        qty12 += line.forecast_qty
        self.qty_month1 = qty1
        self.qty_month2 = qty2
        self.qty_month3 = qty3
        self.qty_month4 = qty4
        self.qty_month5 = qty5
        self.qty_month6 = qty6
        self.qty_month7 = qty7
        self.qty_month8 = qty8
        self.qty_month9 = qty9
        self.qty_month10 = qty10
        self.qty_month11 = qty11
        self.qty_month12 = qty12

    total_first = fields.Float()
    total_second = fields.Float()
    total_third = fields.Float()
    total_fourth = fields.Float()
    total_fifth = fields.Float()
    total_sixth = fields.Float()

    test = fields.Boolean(default=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type='tree', context=None, toolbar=False, submenu=False):
        """
            Purpose: to dynamically display the dates
        """
        # result = super(FlspSalesForecast, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        result = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        current_month = datetime.today().month
        # current_month = 12
        # for line in self:
        #     if line.forecast_line.forecast_date < datetime.today():
        #         line.forecast_line.active = False

        if view_type == 'tree':
            doc = etree.XML(result['arch'])
            if current_month == 12:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name','qty_month12')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name','qty_month1')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name','qty_month2')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name','qty_month3')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name','qty_month4')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name','qty_month5')
                    node.addnext(etree.Element('field', {'string':'November','name':'qty_month11','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'October','name':'qty_month10','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'September', 'name': 'qty_month9', 'optional': 'hide'}))
                    node.addnext(etree.Element('field', {'string':'August','name':'qty_month8','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'July','name':'qty_month7','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'June','name':'qty_month6','optional':'hide'}))
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 1:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month1')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month2')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month3')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month4')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month5')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month6')
                    node.addnext(etree.Element('field', {'string':'December','name':'qty_month12','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'November','name':'qty_month11','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'October','name':'qty_month10','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'September','name':'qty_month9','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'August','name':'qty_month8','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'July','name':'qty_month7','optional':'hide'}))
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 2:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month2')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month3')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month4')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month5')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month6')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month7')
                    node.addnext(etree.Element('field', {'string':'January','name':'qty_month1','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'December','name':'qty_month12','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'November','name':'qty_month11','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'October','name':'qty_month10','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'September','name':'qty_month9','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'August','name':'qty_month8','optional':'hide'}))
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 3:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month3')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month4')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month5')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month6')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month7')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month8')
                    node.addnext(etree.Element('field', {'string': 'February', 'name': 'qty_month2', 'optional': 'hide'}))
                    node.addnext(etree.Element('field', {'string':'January','name':'qty_month1','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'December','name':'qty_month12','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'November','name':'qty_month11','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'October','name':'qty_month10','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'September','name':'qty_month9','optional':'hide'}))
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 4:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month4')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month5')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month6')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month7')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month8')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month9')
                    node.addnext(etree.Element('field', {'string': 'March','name':'qty_month3','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'February', 'name': 'qty_month2', 'optional': 'hide'}))
                    node.addnext(etree.Element('field', {'string':'January','name':'qty_month1','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'December','name':'qty_month12','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'November','name':'qty_month11','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'October','name':'qty_month10','optional':'hide'}))
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 5:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month5')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month6')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month7')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month8')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month9')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month10')
                    node.addnext(etree.Element('field', {'string':'April','name':'qty_month4','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'March','name':'qty_month3','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'February', 'name': 'qty_month2', 'optional': 'hide'}))
                    node.addnext(etree.Element('field', {'string':'January','name':'qty_month1','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'December','name':'qty_month12','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'November','name':'qty_month11','optional':'hide'}))
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 6:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month6')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month7')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month8')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month9')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month10')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month11')
                    node.addnext(etree.Element('field', {'string':'May','name':'qty_month5','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'April','name':'qty_month4','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'March','name':'qty_month3','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'February', 'name': 'qty_month2', 'optional': 'hide'}))
                    node.addnext(etree.Element('field', {'string':'January','name':'qty_month1','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'December','name':'qty_month12','optional':'hide'}))
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 7:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month7')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month8')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month9')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month10')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month11')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month12')
                    node.addnext(etree.Element('field', {'string':'June','name':'qty_month6','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'May','name':'qty_month5','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'April','name':'qty_month4','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'March','name':'qty_month3','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'February', 'name': 'qty_month2', 'optional': 'hide'}))
                    node.addnext(etree.Element('field', {'string':'January','name':'qty_month1','optional':'hide'}))
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 8:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month8')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month9')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month10')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month11')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month12')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month1')
                    node.addnext(etree.Element('field', {'string':'July','name':'qty_month7','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'June','name':'qty_month6','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'May','name':'qty_month5','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'April','name':'qty_month4','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'March','name':'qty_month3','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'February', 'name': 'qty_month2', 'optional': 'hide'}))
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 9:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month9')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month10')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month11')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month12')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month1')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month2')
                    node.addnext(etree.Element('field', {'string': 'August', 'name': 'qty_month8', 'optional': 'hide'}))
                    node.addnext(etree.Element('field', {'string':'July','name':'qty_month7','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'June','name':'qty_month6','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'May','name':'qty_month5','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'April','name':'qty_month4','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'March','name':'qty_month3','optional':'hide'}))
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 10:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month10')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month11')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month12')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month1')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month2')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month3')
                    node.addnext(etree.Element('field', {'string': 'September','name':'qty_month9','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'August', 'name': 'qty_month8', 'optional': 'hide'}))
                    node.addnext(etree.Element('field', {'string':'July','name':'qty_month7','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'June','name':'qty_month6','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'May','name':'qty_month5','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'April','name':'qty_month4','optional':'hide'}))
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 11:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month11')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month12')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month1')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month2')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month3')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month4')
                    node.addnext(etree.Element('field', {'string':'October','name':'qty_month10','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'September','name':'qty_month9','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string': 'August', 'name': 'qty_month8', 'optional': 'hide'}))
                    node.addnext(etree.Element('field', {'string':'July','name':'qty_month7','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'June','name':'qty_month6','optional':'hide'}))
                    node.addnext(etree.Element('field', {'string':'May','name':'qty_month5','optional':'hide'}))
                result['arch'] = etree.tostring(doc, encoding='unicode')

        if view_type == 'form':
            doc = etree.XML(result['arch'])
            if current_month == 12:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name','qty_month12')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name','qty_month1')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name','qty_month2')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name','qty_month3')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name','qty_month4')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name','qty_month5')
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 1:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month1')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month2')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month3')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month4')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month5')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month6')
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 2:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month2')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month3')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month4')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month5')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month6')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month7')
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 3:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month3')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month4')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month5')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month6')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month7')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month8')
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 4:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month4')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month5')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month6')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month7')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month8')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month9')
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 5:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month5')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month6')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month7')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month8')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month9')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month10')
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 6:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month6')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month7')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month8')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month9')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month10')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month11')
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 7:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month7')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month8')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month9')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month10')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month11')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month12')
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 8:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month8')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month9')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month10')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month11')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month12')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month1')
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 9:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month9')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month10')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month11')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month12')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month1')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month2')
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 10:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month10')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month11')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month12')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month1')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month2')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month3')
                result['arch'] = etree.tostring(doc, encoding='unicode')

            elif current_month == 11:
                for node in doc.xpath("//field[@name='total_first']"):
                    node.set('name', 'qty_month11')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_second']"):
                    node.set('name', 'qty_month12')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_third']"):
                    node.set('name', 'qty_month1')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fourth']"):
                    node.set('name', 'qty_month2')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_fifth']"):
                    node.set('name', 'qty_month3')
                result['arch'] = etree.tostring(doc, encoding='unicode')
                for node in doc.xpath("//field[@name='total_sixth']"):
                    node.set('name', 'qty_month4')
                result['arch'] = etree.tostring(doc, encoding='unicode')

        return result

    @api.model
    def get_import_templates(self):
        return [{
                    'label': _('Import Template for Sale Forecast'),
                    'template': '/flspsales_forecast/static/xls/Sales_forecast_template.xlsx'
                }]
    
        
    def button_sale_forecast_lines(self):
        view_id = self.env.ref('flspsales_forecast.flsp_sales_forecast_line_tree').id
        return {
            'name': 'Sales Forecast Lines',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'flsp.sales.forecast.line',
            'view_id': view_id,
            'views': [(view_id, 'tree')],
            'target': 'new',
        }


class FlspSalesForecast(models.Model):
    """
            Class_Name: FlspSalesForecast
            Model_Name: flsp_sales_forecast
            Purpose:    To help create the flsp_sales_forecast
            Date:       Dec/15th/2020/W
            Updated:
            Author:     Sami Byaruhanga
    """

    _name = 'flsp.sales.forecast.line'
    _description = "FLSP Sales Forecast Line"
    order_id = fields.Many2one('flsp.sales.forecast', string='Reference', required=True, ondelete='cascade', index=True, copy=False)

    source = fields.Selection([('S', 'Internal'), ('E', 'External')], string="Source")
    customer = fields.Many2one(
        'res.partner', string='Customer', change_default=True, index=True, tracking=1,
        domain=[('customer_rank', '!=', 0)],)
        # domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", domain=[('customer_rank', '!=', 0)],)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    forecast_qty = fields.Float(string='Quantity')
    # total_forecast_qty = fields.Float(string='Total Quantity', compute="cal_total_forecast")
    forecast_date = fields.Datetime(string='Forecast Date', index=True)

    active = fields.Boolean(default=True) #useful, coz when false the line disappears

    # @api.model
    # def write(self, vals):
    #     print("=======write function=====")
    #     res = super(FlspSalesForecast, self).write(vals)
    #     # for line in self.forecast_date:
    #     self.forecast_date += relativedelta(hours=7)
    #     print(self.forecast_date)
    #     return res

    @api.onchange('forecast_date')
    def _check_date_greater_than_today(self):
        """
            Purpose: To ensure that the forecast date is greater than the current date
            Addon:   feb/01/2021 added ability to add forecast for only 12 months
        """
        end_date = datetime.now() + relativedelta(months=13)
        # print(next_year)
        now = datetime.now()
        current_hour = now.strftime("%H")
        current_min = now.strftime("%M")
        current_sec = now.strftime("%S")
        for line in self:
            if line.forecast_date:
                # line.forecast_date += relativedelta(hours=7)
                line.forecast_date += relativedelta(hour=int(current_hour), minute=int(current_min), second=int(current_sec))
                if line.forecast_date < datetime.today():
                    raise ValidationError("Please enter a future forecast date")
                elif line.forecast_date > end_date:
                    raise ValidationError("Please enter Forecast within the next 13 months only")
                print(line.forecast_date)


##ADD TO SCHEDULED ACTION SO AS TO ARCHIEVE LAST MONTHS RECORDS
# for line in env['flsp.sales.forecast.line'].search([]):
#   for val in line:
#     if val.forecast_date:
#       expire = str(val.forecast_date)  # save so we can print meaningful value
#       year_exp = expire[0:4]
#       year_int = int(year_exp)
#       month_exp = expire[5:7]
#       month_int = int(month_exp)
#       if (year_int < datetime.datetime.today().year) or (val.forecast_date < datetime.datetime.today()):
#         line.write({'active':False})
#         # line.unlink()
#         # active = False
