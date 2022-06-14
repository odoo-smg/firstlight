# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SubstitutionProduct(models.Model):
    _inherit = 'product.template'

    flsp_substitute_ids = fields.One2many('flsp.mrp.substitution', 'product_id', 'Substitutes',
        help="Inform here the Part Numbers that can be use as substitute.")

    flsp_has_substitute = fields.Boolean('Has Substitute', compute='compute_flsp_has_subs')

    @api.depends('flsp_substitute_ids')
    def compute_flsp_has_subs(self):
        for each in self:
            if each.flsp_substitute_ids:
                each.flsp_has_substitute = True
            else:
                each.flsp_has_substitute = False



