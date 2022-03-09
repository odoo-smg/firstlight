# -*- coding: utf-8 -*-
from odoo import api, fields, models

# **********************************************
# Created by: Alexandre Sousa
# Create date: 20220309
# To solve dependency issues
# ***********************************************
class FLSPBasePartner(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True

    # **********************************************
    # Fields copies from flsp-salesorder module
    # ***********************************************
    flsp_default_contact = fields.Boolean(String="Default")
    flsp_shipping_method = fields.Selection([
        ('1', 'FL account and Invoice the Customer'),
        ('2', 'FL account and do not Invoice Customer'),
        ('3', 'Customer carrier choice and account'),
    ], string='Shipping Method', copy=False, store=True)
