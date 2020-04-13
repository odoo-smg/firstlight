# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspmrpbomlines(models.Model):
    _inherit = 'mrp.bom.line'
    _check_company_auto = True

    flsp_plm_valid = fields.Boolean(string="PLM Validated", readonly=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.flsp_plm_valid = self.product_id.flsp_plm_valid
