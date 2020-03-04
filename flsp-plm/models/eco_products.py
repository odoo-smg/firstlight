# -*- coding: utf-8 -*-

from odoo import fields, models


class flspproducts(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    # New fields to control ECO enforcement
    flsp_eco_enforce = fields.Many2one('mrp.eco', string="ECO", store=False)
    flsp_plm_valid   = fields.Boolean(string="PLM Validated", store=False )
