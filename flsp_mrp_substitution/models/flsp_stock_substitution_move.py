# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class FlspSubsStockMove(models.Model):
    _inherit = 'stock.move'

    flsp_substitute = fields.Boolean(string="Substitute", compute='_calc_prod_substitute')

    @api.depends('product_id')
    def _calc_prod_substitute(self):
        bom_id = self.raw_material_production_id.bom_id
        components = self._get_flattened_totals(bom_id)
        for move in self:
            move.flsp_substitute = False
            for line in components:
                if components[line]['prod'] == move.product_id and components[line]['bom_line'] == move.bom_line_id.id:
                    move.flsp_substitute = True

    def _get_flattened_totals(self, bom_id, factor=1, totals=None, level=None):
        if totals is None:
            totals = {}
        for subs in bom_id.flsp_substitution_line_ids:
            totals[len(totals) + 1] = {'prod': subs.product_id, 'bom_line': subs.bom_line_id.id, 'qty': subs.product_qty,
                                       'sub': subs.product_substitute_id, 'sub_qty': subs.product_substitute_qty}
        for line in bom_id.bom_line_ids:
            sub_bom = bom_id._bom_find(product=line.product_id)
            if sub_bom:
                if sub_bom.type == 'phantom':
                    for subs in sub_bom.flsp_substitution_line_ids:
                        totals[len(totals) + 1] = {'prod': subs.product_id, 'bom_line': subs.bom_line_id.id, 'qty': subs.product_qty,
                                                   'sub': subs.product_substitute_id, 'sub_qty': subs.product_substitute_qty}
                self._get_flattened_totals(sub_bom, 1, totals, 2)
        return totals
