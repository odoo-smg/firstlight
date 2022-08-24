# -*- coding: utf-8 -*-
from odoo import api, fields, models

class FlspSalesDeliveryMove(models.Model):
    """
            Class_Name: FlspSalesDeliveryMove
            Model_Name: To create the field for the Sales Delivery Report
            Purpose:    To help link the SOs that need to be shipped together
            Date:       November/1st/Monday/2021
            Updated:
            Author:     Alexandre Sousa
    """
    _inherit = "stock.move"
    _check_company_auto = True

    flsp_order_date = fields.Datetime(string='Sales Confirmation', store=True, compute="_compute_flsp_order_date")
    flsp_ship_with = fields.Char(string="Ship with SO", compute="_compute_flsp_ship_with")
    picking_policy = fields.Selection([
        ('direct', 'Yes'),
        ('one', 'No')],
        string='Allow Backorders', compute="_compute_flsp_ship_with"
        ,help="If you deliver all products at once, the delivery order will be scheduled based on the greatest "
        "product lead time. Otherwise, it will be based on the shortest.")


    def _compute_flsp_order_date(self):
        for each in self:
            if each.picking_id.sale_id:
                each.flsp_order_date = each.picking_id.sale_id.date_order
            else:
                each.flsp_order_date = False

    def _compute_flsp_ship_with(self):
        for each in self:
            if each.picking_id.sale_id:
                each.flsp_ship_with = each.picking_id.sale_id.flsp_ship_with
                each.picking_policy = each.picking_id.sale_id.picking_policy
            else:
                each.flsp_ship_with = False
                each.picking_policy = False
