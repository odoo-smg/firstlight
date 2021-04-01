# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class product_template(models.Model):
    """
        class_name: product_template
        model_name: product.template
        Purpose:    To add a specific location on the product
        Date:       March.31st.2021.W
        Author:     Sami Byaruhanga
    """
    _inherit = 'product.template'

    flsp_sd_location = fields.Many2one('stock.location', string='Standard Location')


class FlspStockMoveLineSdLocation(models.Model):
    """
        class_name: FlspStockMoveLineSdLocation
        model_name: stock.move.line
        Purpose:    To add a specific location on the stock detailed operation
        Date:       April.1st.2021.R
        Author:     Sami Byaruhanga
    """
    _inherit = 'stock.move.line'
    flsp_sd_location = fields.Many2one(related='product_id.product_tmpl_id.flsp_sd_location')