# -*- coding: utf-8 -*-

from odoo import fields, models


class producteco(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    flsp_allow_upd = fields.Boolean(string="Allow Edit")
    flsp_eco_id = fields.Many2one('mrp.eco', 'ECO', check_company=True)
    
