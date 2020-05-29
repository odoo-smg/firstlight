# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Flspcompany(models.Model):
    _inherit = "res.company"
    _check_company_auto = True

    so_flsp_max_percent_approval = fields.Float(string="Max Discount Allowed", help="Minimum discount percent allowed")
    flspsppepp_category_id = fields.Many2one('product.category', string="Product Category", help="Category of products for School PPE Purchase Program")
    flsp_percent_sppepp = fields.Float(string="Percent of Deposit")
    flspsppepp_product_id = fields.Many2one('product.product', string="Product", help="Product used to add the 3% increase due to Credit Card Payment")
