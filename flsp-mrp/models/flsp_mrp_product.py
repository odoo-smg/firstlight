# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions

import logging
_logger = logging.getLogger(__name__)

class FlspMrpProduct(models.Model):
    _inherit = 'product.product'
    
    flsp_wip_qty = fields.Float('WIP Qty', default=0.0, digits='Product Unit of Measure', readonly=True, store=False, compute='get_wip_qty')
    flsp_stock_qty = fields.Float('Stock Qty', default=0.0, digits='Product Unit of Measure', readonly=True, store=False, compute='get_stock_qty')

    def get_wip_qty(self):
        """ 
            Purpose: get the WIP qty for the product
        """
        self.ensure_one()
        pa_wip_qty = 0

        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')]).parent_path
        if not pa_location:
            raise UserError('WIP Stock Location is missing')
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location+'%')]).ids
        if not pa_wip_locations:
            raise UserError('WIP Stock Location is missing')

        stock_quant = self.env['stock.quant'].search(
            ['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', self.id)])
        for stock_lin in stock_quant:
            pa_wip_qty += stock_lin.quantity

        self.flsp_wip_qty = pa_wip_qty
        return pa_wip_qty
    
    @api.depends('qty_available', 'flsp_wip_qty')
    def get_stock_qty(self):
        self.flsp_stock_qty = self.qty_available - self.flsp_wip_qty
        return self.flsp_stock_qty