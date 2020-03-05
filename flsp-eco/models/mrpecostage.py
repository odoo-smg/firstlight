# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspmrpecostage(models.Model):
    _inherit = 'mrp.eco.stage'
    _check_company_auto = True

    # New fields to control ECO enforcement
    flsp_allow_change = fields.Boolean(string="Allow Change Product")
