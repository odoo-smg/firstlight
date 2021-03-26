# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspmrpeco(models.Model):
    _inherit = 'mrp.eco'
    _check_company_auto = True

    # New fields to control ECO enforcement
    flsp_allow_change = fields.Boolean(string="Allow Product Change", compute='_allow_change')
    flsp_product_valid = fields.Boolean(string="Product Validated before", compute='_product_valid')
    flsp_bom_valid = fields.Boolean(string="BOM Validated before", compute='_bom_valid')

    @api.depends('stage_id')
    def _allow_change(self):
        self.flsp_allow_change = self.stage_id.flsp_allow_change

    @api.depends('product_tmpl_id')
    def _product_valid(self):
        self.flsp_product_valid = self.product_tmpl_id.flsp_plm_valid

    @api.depends('bom_id')
    def _bom_valid(self):
        self.flsp_bom_valid = self.bom_id.flsp_bom_plm_valid

    @api.constrains('stage_id')
    def _check_done_eco(self):
        for record in self:
            if record.state == "done" and self.stage_id.final_stage != True:
                raise exceptions.ValidationError("You cannot change stage once the ECO is done.")

    @api.onchange('product_tmpl_id')
    def _onchange_type_id(self):
        npi_stage = self.env['mrp.eco.type'].search([('name', '=', 'New Product Introduction')], limit=1).id
        pi_stage = self.env['mrp.eco.type'].search([('name', '=', 'Product Improvement')], limit=1).id
        pi_first_stage = self.env['mrp.eco.stage'].search([('type_id', '=', pi_stage)], limit=1).id
        npi_first_stage = self.env['mrp.eco.stage'].search([('type_id', '=', npi_stage)], limit=1).id
        for record in self:
            if record.product_tmpl_id.flsp_plm_valid:
                record.type_id = pi_stage
                record.stage_id = pi_first_stage
            else:
                record.type_id = npi_stage
                record.stage_id = npi_first_stage

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        """
            Date:    Mar/26th/2021
            Purpose: OVERWRITE the same method in file "mrp_eco.py" for Model "mrp.eco"
                    to reset self.bom_id when no BOM is associated with the selected product
            Assumption: Value "False" is the default value for no BOM associated
            Author: Perry He
        """
        if self.product_tmpl_id.bom_ids:
            self.bom_id = self.product_tmpl_id.bom_ids.ids[0]
        else:
            self.bom_id = False
