# -*- coding: utf-8 -*-
from odoo import models, fields


class FlspBackorder(models.Model):

    _inherit = "product.category"
    _check_company_auto = True

    flsp_sale_target_ids = fields.One2many(
        'flsp.sale.target.category', 'category_id', 'Sale Target',
        help="Inform here the Sale Target for the product category.")

    flsp_weekly_report = fields.Boolean("Weekly Report")
    flsp_name_report = fields.Char('Report Category Name')
    flsp_report_color = fields.Char('Report Color')
