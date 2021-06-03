# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class FlspBfStockMove(models.Model):
    _inherit = 'stock.move'

    flsp_backflush = fields.Boolean(string="Backflush", compute='_calc_prod_backflush')

    @api.depends('product_id')
    def _calc_prod_backflush(self):
        for move in self:
            move.flsp_backflush = move.product_id.product_tmpl_id.flsp_backflush
