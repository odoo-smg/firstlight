# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspproductproducts(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_eco_count = fields.Integer(compute='_compute_flsp_eco', string='Qty ECOs')

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
        action = self.env.ref('flsp-eco.action_view_eco_product').read()[0]
        action['domain'] = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
        return action
