# -*- coding: utf-8 -*-

from odoo import fields, models, api


class customerproduct(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    _check_company_auto = True

    customerscode_ids = fields.One2many(
        'flspstock.customerscode', 'product_id', 'Customer Part Number',
        help="Inform here the Part Numbers assigned by the customer.")
