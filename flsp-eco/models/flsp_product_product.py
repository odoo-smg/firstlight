# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspproductproducts(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_eco_count = flsp_open_po_qty = fields.Integer(compute='_compute_flsp_eco', string='Qty Open PO')

    def _compute_flsp_eco(self):
        domain = [
            ('product_tmpl_id', '=', self.product_tmpl_id.id)
        ]
        product_ecos = self.env['mrp.eco'].search(domain)
        for eco in product_ecos:
            self.flsp_eco_count += 1
        if not self.flsp_eco_count:
            self.flsp_eco_count = 0

    def action_flsp_view_eco(self):
        product_prd = self.env['product.product'].search([('product_tmpl_id', 'in', self.ids)])
        action = self.env.ref('flsppurchase.action_purchase_order_line_all').read()[0]
        action['domain'] = ['&', ('product_id', '=', product_prd.ids), ('flsp_open_qty', '>', 0)]
        return action

#        action = self.env.ref('action_view_eco_product').read()[0]
#        action['domain'] = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
#        return action
