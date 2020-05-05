# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flsppurchase(models.Model):
    _inherit = 'purchase.order.line'
    _check_company_auto = True

    flsp_vendor_code = fields.Char('Vendor Product Code', compute='_calc_vendor_code')

    @api.depends('product_id')
    def _calc_vendor_code(self):
        self.ensure_one()
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom)
        if seller:
            self.flsp_vendor_code = seller.product_code
        else:
            self.flsp_vendor_code = '1'
#        for line in self:
#            if not line.flsp_vendor_code:
#                line.flsp_vendor_code = '2'
#            else:
#                line.flsp_vendor_code = '3'
