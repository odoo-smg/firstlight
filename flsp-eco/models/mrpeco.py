# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspmrpeco(models.Model):
    _inherit = 'mrp.eco'
    _check_company_auto = True

    # New fields to control ECO enforcement
    flsp_allow_change = fields.Boolean(string="Allow Change", compute='_allow_change')

    @api.depends('stage_id')
    def _allow_change(self):
        self.flsp_allow_change = self.stage_id.	allow_apply_change
