# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class flspmrpbom(models.Model):
    _inherit = 'mrp.bom'
    _check_company_auto = True

    # New fields to control ECO enforcement
    flsp_eco_enforce = fields.Many2one('mrp.eco', string="ECO", store=False)
    flsp_bom_plm_valid = fields.Boolean(string="PLM Validated")

    @api.onchange('flsp_eco_enforce')
    def flsp_eco_enforce_onchange(self):
        self.flsp_plm_valid = False
        return {
            'value': {
                'flsp_bom_plm_valid': False
            },
        }

    def copy(self, default=None):
        default = dict(default or {})
        default['flsp_bom_plm_valid'] = False
        return super(flspmrpbom, self).copy(default)


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
