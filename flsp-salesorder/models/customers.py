# -*- coding: utf-8 -*-

from odoo import fields, models


class flspcustomer(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True

    flsp_user_id = fields.Many2one('res.users', string="Inside Salesperson")
    flsp_dss_user_id = fields.Many2one('res.users', string="Dealer Specialist")
    flsp_shipping_method = fields.Selection([
        ('1', 'FL account and Invoice the Customer'),
        ('2', 'FL account and do not Invoice Customer'),
        ('3', 'Customer carrier choice and account'),
        ], string='Shipping Method', copy=False, store=True)

    flsp_carrier_account = fields.Char(string="Carrier Account")

    flsp_default_contact = fields.Boolean(string="Default")

    _sql_constraints = [
        ('customer_name_unique_flsp',
         'UNIQUE(name)',
         "The Name must be unique. Please, check the current list of customers."),
    ]
