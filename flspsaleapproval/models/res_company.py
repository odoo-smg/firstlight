# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Flspcompany(models.Model):
    _inherit = "res.company"
    _check_company_auto = True

    so_flsp_max_percent_approval = fields.Float(string="Max Discount Allowed", help="Minimum discount percent allowed")
    
