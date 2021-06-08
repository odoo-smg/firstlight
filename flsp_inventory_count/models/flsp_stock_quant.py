# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from odoo.exceptions import ValidationError

class FlspStockQuant(models.Model):
    _inherit = 'stock.quant'
    # _check_company_auto = True

    default_code = fields.Char(String='Product', related="product_id.default_code")
    flsp_check_inv = fields.Boolean('Can edit', compute='_compute_flsp_inv')

    def _compute_flsp_inv(self):
        if self.user_has_groups('flsp_inventory_count.group_iventory_count_manager'):
            self.flsp_check_inv = True
        else:
            self.flsp_check_inv = False
