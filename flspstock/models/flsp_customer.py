# -*- coding: utf-8 -*-

from odoo import fields, models


class flspstockcustomer(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True


    #flsp_show_packing = fields.Boolean(string="Show Packaging on Packing List")
