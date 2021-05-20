# -*- coding: utf-8 -*-

from odoo import fields, models, api


class FlspSerialMrpPrd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_serial_mrp = fields.Boolean(string="Lot/Serial on MO", copy=False)
