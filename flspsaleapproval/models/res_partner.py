# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspsalespartner(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True

    @api.model
    def _default_flsp_sale_currency(self):
        currency_id = self.env['res.currency'].search([('name',  '=', 'USD')])
        return currency_id

    flsp_sale_currency = fields.Many2one('res.currency', string='Sale Currency', default=_default_flsp_sale_currency, required=True)
    flsp_sale_type = fields.Selection([
        ('1', 'OEM'),
        ('2', 'Dealer'),
        ('3', 'School'),
        ('4', 'Contractor'),
        ], string='Sale Group',  default='3', required=True)
