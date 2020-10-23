# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Terms(models.Model):
    """
        class_name: Terms
        model_name: flspticketsystem.category
        Purpose:    To help add terms and conditions for purchases
        NOTE:       To view all u need is add security access!
        Date:       Oct/22nd/2020/Thur
        Author:     Sami Byaruhanga
    """

    _name = 'flsp.terms'
    _description = "FlspTerms"

    _rec_name = "flsp_term_name" #Helps to name the form view with this name
    flsp_term_name = fields.Char(string="Name", required=True)
    flsp_terms_and_conditions = fields.Html(string='Terms and Conditions')


class vendor_template(models.Model):
    """
        class_name: vendor_template
        model_name: inherits the vendor template
        Purpose:    To add a selectable field for terms and conditions
        Date:       Oct/22nd/2020/Thur
        Author:     Sami Byaruhanga

    """
    # _inherit = 'product.template'
    _inherit = 'res.partner'

    terms = fields.Many2one('flsp.terms', string='Flsp Terms', ondelete='cascade',)
