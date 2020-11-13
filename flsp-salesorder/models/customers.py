# -*- coding: utf-8 -*-

from odoo import fields, models


class flspcustomer(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True

    flsp_user_id = fields.Many2one('res.users', string="Salesperson 2")

    _sql_constraints = [
        ('customer_name_unique_flsp',
         'UNIQUE(name)',
         "The Name must be unique. Please, check the current list of customers."),
    ]
