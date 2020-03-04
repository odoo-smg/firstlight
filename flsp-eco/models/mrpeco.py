# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspmrpeco(models.Model):
    _inherit = 'mrp.eco'
    _check_company_auto = True

    # New fields to control ECO enforcement
    flsp_allow_change = fields.Boolean(string="Allow Change", readonly=True)

    @api.onchange('stage_id')
    def stage_id_onchange(self):
        return_val = self.stage_id.	allow_apply_change
        self.flsp_allow_change = return_val
        return {
            'value': {
                'flsp_allow_change': return_val
            },
        }
