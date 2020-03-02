# -*- coding: utf-8 -*-

from odoo import fields, models


class flspcustomer(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True

    flsp_user_id = Many2one('res.user', string="Salesperson 2")
