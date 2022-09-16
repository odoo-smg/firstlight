# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class FlspMrpProduct(models.Model):
    _inherit = 'product.product'

    flsp_wip_qty = fields.Float('WIP Qty', default=0.0, digits='Product Unit of Measure', readonly=True, store=False, compute='get_wip_qty')
    flsp_stock_qty = fields.Float('Stock Qty', default=0.0, digits='Product Unit of Measure', readonly=True, store=False, compute='get_stock_qty')
    flsp_available_qty = fields.Float('Available Qty', default=0.0, digits='Product Unit of Measure', readonly=True, store=False, compute='get_available_qty')

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

    @api.depends('qty_available', 'virtual_available')
    def get_available_qty(self):
        # according to rules in Ticket 413
        for record in self:
            if record.virtual_available < 0:
                record.flsp_available_qty = 0
            elif 0 == record.virtual_available:
                record.flsp_available_qty = 0
            elif record.virtual_available > 0 and record.virtual_available <= record.qty_available:
                record.flsp_available_qty = record.virtual_available
            else:
                record.flsp_available_qty = record.qty_available


class FlspMrpProductTemplate(models.Model):
    _inherit = 'product.template'

    flsp_mrp_delivery_location = fields.Many2one("stock.location", "Drop off Location (informative)", domain="[ '|', ('active','=',True),  ('active','=',False)]")
    flsp_mrp_delivery_method = fields.Selection([
        ('kanban', 'Kanban'),
        ('kitting', 'Kitting')], string='Method', copy=False,
        store=True,
        help=" * Kanban will be replenished using the report Kanban.\n"
             " * Kitting will be transferred from Stock to WIP based on MOs.\n")
