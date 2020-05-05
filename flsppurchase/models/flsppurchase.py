# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flsppurchase(models.Model):
    _inherit = 'purchase.order.line'
    _check_company_auto = True

    flsp_vendor_code = fields.Char('Vendor Product Code', compute='_calc_vendor_code')

    @api.depends('product_id')
    def _calc_vendor_code(self):
        date = fields.Date.context_today(self)
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        res = self.env['product.supplierinfo']
        sellers = self.product_id.seller_ids.filtered(lambda s: s.name.active).sorted(lambda s: (s.sequence, -s.min_qty, s.price))
        quantity_uom_seller = self.product_qty
        if self.env.context.get('force_company'):
            sellers = sellers.filtered(lambda s: not s.company_id or s.company_id.id == self.env.context['force_company'])

        for seller in sellers:
            if quantity_uom_seller and uom_id and uom_id != seller.product_uom:
                quantity_uom_seller = uom_id._compute_quantity(quantity_uom_seller, seller.product_uom)
            if seller.date_start and seller.date_start > date:
                continue
            if seller.date_end and seller.date_end < date:
                continue
            if partner_id and seller.name not in [self.partner_id, self.partner_id.parent_id]:
                continue
            if float_compare(quantity_uom_seller, seller.min_qty, precision_digits=precision) == -1:
                continue
            if seller.product_id and seller.product_id != self.product_id:
                continue
            if not res or res.name == seller.name:
                res |= seller
        vendor = res.sorted('price')[:1]

        if vendor:
            self.flsp_vendor_code = vendor.product_code
        else:
            self.flsp_vendor_code = '1'
