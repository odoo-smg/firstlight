# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspmrpeco(models.Model):
    _inherit = 'mrp.eco'
    _check_company_auto = True

    # New fields to control ECO enforcement
    flsp_allow_change = fields.Boolean(string="Allow Product Change", compute='_allow_change')
    flsp_product_valid = fields.Boolean(string="Product Validated before", compute='_product_valid')

    @api.depends('stage_id')
    def _allow_change(self):
        self.flsp_allow_change = self.stage_id.flsp_allow_change

    @api.depends('product_tmpl_id')
    def _product_valid(self):
        self.flsp_product_valid = self.product_tmpl_id.flsp_plm_valid

    @api.constrains('stage_id')
    def _check_done_eco(self):
        for record in self:
            if record.state == "done" and self.stage_id.final_stage != True:
                raise exceptions.ValidationError("You cannot change stage once the ECO is done.")

    @api.onchange('product_tmpl_id')
    def _onchange_type_id(self):
        npi_stage = self.env['mrp.eco.type'].search([('name', '=', 'New Product Introduction')], limit=1).id
        pi_stage = self.env['mrp.eco.type'].search([('name', '=', 'Product Improvement')], limit=1).id
        for record in self:
            if record.product_tmpl_id.flsp_plm_valid:
                record.type_id = pi_stage
            else:
                record.type_id = npi_stage
