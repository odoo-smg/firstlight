# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from odoo.exceptions import ValidationError

class FlspStockQuant(models.Model):
    _inherit = 'stock.quant'
    _check_company_auto = True

    default_code = fields.Char(String='Product', related="product_id.default_code")
