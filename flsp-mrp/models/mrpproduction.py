# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspproduction(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain="[('flsp_plm_valid', '=', True), ('bom_ids', '!=', False), ('bom_ids.active', '=', True), ('bom_ids.type', '=', 'normal'), ('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        readonly=True, required=True, check_company=True,
        states={'draft': [('readonly', False)]})


    @api.constrains('product_id')
    def _check_done_eco(self):
        for record in self:
            if record.product_id.flsp_plm_valid != True:
                raise exceptions.ValidationError("You cannot use products that haven't been PLM Validated yet.")
