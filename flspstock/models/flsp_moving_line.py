# -*- coding: utf-8 -*-

from odoo import fields, models, api


class flspmovingline(models.Model):
    _inherit = 'stock.move.line'
    _check_company_auto = True

    flsp_lot_name = fields.Char("Lot name", compute='flsp_comp_lot_name')
    flsp_part_num = fields.Char('Part#', related='product_id.default_code', readonly=True)

    @api.depends('lot_id')
    def flsp_comp_lot_name(self):
        for line in self:
            if line.lot_id:
                line.flsp_lot_name = line.lot_id.name
            else:
                line.flsp_lot_name = ""
