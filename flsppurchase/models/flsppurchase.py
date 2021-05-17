# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import float_compare


class flsppurchase(models.Model):
    _inherit = 'purchase.order.line'
    _check_company_auto = True

    flsp_vendor_code = fields.Char('Vendor Part #')
    flsp_open_qty = fields.Float('Open Qty', compute='_open_qty_to_receive', store=True)
    flsp_product_code = fields.Char('Part #', compute='_product_code_purchase_line', store=True)
    flsp_product_desc = fields.Char('Description', compute='_product_desc_purchase_line', store=True)

    @api.onchange('product_id', 'product_qty', 'product_uom')
    def _onchange_flsp_product(self):
        for line in self:
            if not line.product_id:
                return
            params = {'order_id': self.order_id}
            vendor = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and self.order_id.date_order.date(),
                uom_id=line.product_uom,
                params=params)
            if vendor:
                line.flsp_vendor_code = vendor.product_code

    @api.depends('product_qty', 'qty_received')
    def _open_qty_to_receive(self):
        for line in self:
            line.flsp_open_qty = line.product_qty - line.qty_received


    def _product_code_purchase_line(self):
        for line in self:
            line.flsp_product_code = line.product_id.default_code

    def _product_desc_purchase_line(self):
        for line in self:
            line.flsp_product_desc = line.product_id.name
