# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspsalespartner(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True

    flsp_sale_currency = fields.Many2one('res.currency', string='Sale Currency')
    flsp_sale_type = fields.Selection([
        ('1', 'OEM'),
        ('2', 'Dealer'),
        ('3', 'School'),
        ('4', 'Contractor'),
        ], string='Sale Group',  default='4', required=True)

