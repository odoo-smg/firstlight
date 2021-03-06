# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspmrpbomlines(models.Model):
    _inherit = 'mrp.bom.line'
    _check_company_auto = True

    flsp_plm_valid = fields.Boolean(string="PLM Validated", readonly=True, compute='_calc_plm_valid')

    @api.depends('product_id', 'bom_id')
    def _calc_plm_valid(self):
        for line in self:
            if not line.product_id:
                line.flsp_plm_valid = False
            else:
                line.flsp_plm_valid = line.product_id.flsp_plm_valid

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.flsp_plm_valid = self.product_id.flsp_plm_valid
            self.product_uom_id = self.product_id.uom_id

    @api.constrains('product_id')
    def _check_product_id(self):
        for record in self:
            if record.product_id.product_tmpl_id == self.bom_id.product_id:
                raise exceptions.ValidationError("You cannot use the same product to produce as components.")
            if record.product_id.product_tmpl_id == record.bom_id.product_id:
                raise exceptions.ValidationError("You cannot use the same product to produce as components.")
