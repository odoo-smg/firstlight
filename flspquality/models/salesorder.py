# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class QualitySalesOrder(models.Model):
    _inherit = "sale.order"
    _check_company_auto = True

    flsp_warranty = fields.Boolean(string="Warranty Order")
