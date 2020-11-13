# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Flsp_Credit_Report(models.Model):
    """
        Class_Name: Flsp_Credit_Report
        Model_Name: inherits the res.partner
        Purpose:    To help create FLSP credit report field on customers
        Date:       Nov/4th/Wednesday/2020
        Updated:
        Author:     Sami Byaruhanga
    """

    _inherit = 'res.partner'

    flsp_credit_report = fields.Many2many('ir.attachment', string='Credit Report',
        help='Add any credit report attachments that will help in solving your request')

    # flsp_credit_report = fields.Binary(string="Credit Report", attachment=True)
