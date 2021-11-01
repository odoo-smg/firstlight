# -*- coding: utf-8 -*-
from odoo import api, fields, models

class FlspSalesDeliverySales(models.Model):
    """
            Class_Name: FlspSalesDeliverySales
            Model_Name: To create the field for the Sales Delivery Report
            Purpose:    To help link the SOs that need to be shipped together
            Date:       November/1st/Monday/2021
            Updated:
            Author:     Alexandre Sousa
    """
    _inherit = "sale.order"
    _check_company_auto = True

    flsp_ship_with = fields.Char(string="Ship with SO")
    picking_policy = fields.Selection([
        ('direct', 'Yes'),
        ('one', 'No')],
        string='Allow Backorders', required=True, readonly=True, default='direct',
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
        ,help="If you deliver all products at once, the delivery order will be scheduled based on the greatest "
        "product lead time. Otherwise, it will be based on the shortest.")

