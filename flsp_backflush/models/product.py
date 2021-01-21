# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Backflushproducts(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    flsp_backflush = fields.Boolean(string="Backflush", default=True)
