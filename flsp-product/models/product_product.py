# -*- coding: utf-8 -*-

from odoo import fields, models


class smgproductprd(models.Model)
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_acc_valid   = fields.Boolean(string="Acconting Validated", readonly=True)
