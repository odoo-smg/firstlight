# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models


class FlspCostDetail(models.Model):
    """
        Class_Name: FlspCostDetail
        Model_Name: flsp.cost.detail
        Purpose:    Create a view for Cost Detail Report
        Date:       October/12th/Tuesday/2021
        Updated:
        Author:     Alexandre Sousa
    """
    _name = 'flsp.cost.detail'
    _description = 'Cost Detail Report'

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')
    date = fields.Datetime(string="Date", readonly=True)
    location_id = fields.Many2one('stock.location', string='Source', readonly=True)
    location_dest_id = fields.Many2one('stock.location', string='Destination', readonly=True)
    reference = fields.Char(string="Reference", readonly=True)
    origin = fields.Char(string="Origin", readonly=True)
    qty_done = fields.Float(string='Qty Moved', readonly=True)
    price_unit = fields.Float(string='Price Unit', readonly=True)

    product_qty = fields.Float(string='Product Qty', readonly=True)

    stock_move_line_id = fields.Many2one('stock.move.line', string='Move Line Id', readonly=True)
    stock_valuation_layer_id = fields.Many2one('stock.valuation.layer', string='Stock Valuation Layer Id', readonly=True)

    value = fields.Float(string='Value', readonly=True)
    unit_cost = fields.Float(string='Valuation Cost', readonly=True)

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)  ###

    balance = fields.Float(string='Balance', readonly=True)
    cost = fields.Float(string='Unit Cost', readonly=True, digits='Product Price')
    seq = fields.Integer(string='Sequence', readonly=True)


