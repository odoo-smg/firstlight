# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspproducttmplsales(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    flsp_tariff_number = fields.Char(string='Tariff Number')
