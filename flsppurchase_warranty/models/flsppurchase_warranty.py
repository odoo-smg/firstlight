# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FlspPurchaseWarranty(models.Model):
    """
        class_name: FlspPurchaseWarranty
        model_name: inherits purchase.order
        Purpose:    To Help account for warranty if dropshiping
        Date:       Feb/10th/W/2021
        Author:     Sami Byaruhanga
    """
    _inherit = 'purchase.order'

    flsp_warranty = fields.Boolean(string="Flsp Warranty")


