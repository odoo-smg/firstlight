# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import float_compare


class flsppurchase(models.Model):
    _inherit = 'purchase.order.line'
    _check_company_auto = True

    flsp_vendor_code = fields.Char('Vendor Part #')

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