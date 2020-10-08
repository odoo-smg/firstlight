# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspmrpecotype(models.Model):
    _inherit = 'mrp.eco.type'
    _check_company_auto = True

    # New fields to control ECO enforcement
    flsp_plm_valid = fields.Boolean(string="Product Validated Only")
