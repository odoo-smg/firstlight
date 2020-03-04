# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspmrpeco(models.Model):
    _inherit = 'mrp.eco'
    _check_company_auto = True

    # New fields to control ECO enforcement
    flsp_allow_change = fields.Boolean(string="Allow Product Change", compute='_allow_change')

    @api.depends('stage_id')
    def _allow_change(self):
        self.flsp_allow_change = self.stage_id.flsp_allow_change

    @api.constrains('stage_id')
    def _check_done_eco(self):
        for record in self:
            if record.state == "done":
                raise exceptions.ValidationError("You cannot change stage once the ECO is done.")
