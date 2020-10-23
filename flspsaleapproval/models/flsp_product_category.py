# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspproductcategory(models.Model):
    _inherit = 'product.category'
    _check_company_auto = True

    flsp_tariff_number = fields.Char(string='Tariff Number')
