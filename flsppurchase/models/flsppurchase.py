# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flsppurchase(models.Model):
    _inherit = 'purchase.order.line'
    _check_company_auto = True

    flsp_vendor_code = fields.Char('Vendor Product Code', compute='_calc_vendor_code')

    @api.depends('product_id')
    def _calc_vendor_code(self):
        self.ensure_one()
        for line in self:
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order.date(),
                uom_id=line.product_uom)
            if seller:
                line.flsp_vendor_code = seller.product_code
            else:
                line.flsp_vendor_code = '1'
#            if not line.flsp_vendor_code:
#                line.flsp_vendor_code = '2'
#            else:
#                line.flsp_vendor_code = '3'
