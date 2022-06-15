# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class FlspMrpSubstitutionBom(models.Model):
    _inherit = 'mrp.bom'

    flsp_substitution_line_ids = fields.One2many('flsp.mrp.substitution.line', 'flsp_bom_id', string='Components', copy=True)
    flsp_bom_products_ids = fields.One2many('product.product', string='Bom Products', compute='_compute_bom_products_ids')

    @api.depends('bom_line_ids')
    def _compute_bom_products_ids(self):

        prd_ids = []
        for line in self.bom_line_ids:
            if line.product_id and line.flsp_substitute:
                prd_ids.append(line.product_id.id)
        if len(prd_ids) > 0:
            self.flsp_bom_products_ids = self.env["product.product"].search([("id", "in", prd_ids)])
        else:
            self.flsp_bom_products_ids = False

    def flsp_create_product_subs(self, bom_id):
        if bom_id.flsp_substitution_line_ids:
            for each in self.flsp_substitution_line_ids:
                #check substitution part
                product_subs = each.product_id.product_tmpl_id.flsp_substitute_ids
                has_prod_sub = False
                if product_subs:
                    for prd_sub in product_subs:
                        if prd_sub.product_substitute_id.id == each.product_substitute_id.id:
                            if not prd_sub.substituting:
                                prd_sub.substituting = True
                            has_prod_sub = True
                if not has_prod_sub:
                    self.env['flsp.mrp.substitution'].create({
                        'product_id': each.product_id.product_tmpl_id.id,
                        'product_substitute_id': each.product_substitute_id.id,
                        'substituting': True,
                    })

    def write(self, vals):
        res = super(FlspMrpSubstitutionBom, self).write(vals)
        self.flsp_create_product_subs(self)
        return res
