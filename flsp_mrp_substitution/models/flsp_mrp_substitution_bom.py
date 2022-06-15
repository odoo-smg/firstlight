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
