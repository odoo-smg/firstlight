# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flsppurchase(models.Model):
    _inherit = 'purchase.order.line'
    _check_company_auto = True

    flsp_vendor_code = fields.Char('Vendor Product Code', compute='_calc_vendor_code')

    @api.onchange('product_qty', 'product_uom', 'product_id')
    def _onchange_flsp_product(self):
        if not self.product_id:
            return
        params = {'order_id': self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        if not seller:
            return
        self.flsp_vendor_code = seller.product_code

    @api.depends('product_qty', 'product_uom', 'product_id')
    def _calc_vendor_code(self):
        for line in self:
            if line.product_id & line.product_uom & line.product_qty:
                params = {'order_id': self.order_id}
                seller = line.product_id._select_seller(
                    partner_id=self.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and self.order_id.date_order.date(),
                    uom_id=line.product_uom,
                    params=params)
                if seller:
                    line.flsp_vendor_code = seller.product_code
