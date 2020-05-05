# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flsppurchase(models.Model):
    _inherit = 'purchase.order.line'
    _check_company_auto = True

    flsp_vendor_code = fields.Char('Vendor Product Code', compute='_calc_vendor_code')

    @api.depends('product_qty', 'product_uom', 'product_id')
    def _calc_vendor_code(self):
        params = {'order_id': self.order_id}
        for line in self:
            if line.flsp_vendor_code:
                line.flsp_vendor_code = line.flsp_vendor_code+1
            else:
                line.flsp_vendor_code = 1
