# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspProductionStructure(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    def button_flsp_bom_structure(self):
        action = self.env.ref('flsp_mrp_structure.action_report_flsp_mo_bom').read()[0]
        return action
