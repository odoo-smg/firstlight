# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspmrpbomlines(models.Model):
    _inherit = 'mrp.bom.line'
    _check_company_auto = True

    @api.constrains('product_id')
    def _check_product_id(self):
        for record in self:
            if record.product_id.product_tmpl_id == self.bom_id.product_id:
                raise exceptions.ValidationError("You cannot use the same product to produce as components.")
            if record.product_id.product_tmpl_id == record.bom_id.product_id:
                raise exceptions.ValidationError("You cannot use the same product to produce as components.")
