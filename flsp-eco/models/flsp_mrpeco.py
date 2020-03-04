# -*- coding: utf-8 -*-

from odoo import fields, models


class mrpeco(models.Model):
    #_inherit = 'mrp.eco'
    #_check_company_auto = True

    # New fields to control ECO enforcement
    #flsp_allow_change = fields.Boolean(string="Allow Change", readonly=True)
