# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Payment(models.Model):
    """
        class_name: Payment
        model_name: flsp.payment
        Purpose:    To help add payment terms to vendors
        NOTE:       To view all u need is add security access!
        Date:       Oct/27th/2020/Tuesday
        Author:     Sami Byaruhanga
    """

    _name = 'flsp.payment'
    _description = "Flsp Payment Terms"

    _rec_name = "flsp_payement_terms" #Helps to name the form view with this name
    flsp_payement_terms = fields.Char(string="Payment Term", required=True)
    flsp_description = fields.Char(string='Description')


class vendor_temp(models.Model):
    """
        class_name: vendor_temp
        model_name: inherits the vendor template
        Purpose:    To add a selectable field for Payment terms
        Date:       Oct/27th/2020/Tuesday
        Author:     Sami Byaruhanga
    """
    # _inherit = 'product.template'
    _inherit = 'res.partner'

    payment_terms = fields.Many2one('flsp.payment', string='Payment Terms', ondelete='cascade',)
