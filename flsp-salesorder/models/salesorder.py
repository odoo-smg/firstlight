# -*- coding: utf-8 -*-

from odoo import fields, models


class flspsalesorder(models.Model):
    _inherit = 'sale.order'
    _check_company_auto = True

    flsp_so_user_id = fields.Many2one('res.users', string="Salesperson 2")
