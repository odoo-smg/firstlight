# -*- coding: utf-8 -*-

from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'

    flsp_part_init = fields.Char(string="First digit part #")
