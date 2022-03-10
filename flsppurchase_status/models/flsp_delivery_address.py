# -*- coding: utf-8 -*-
from odoo import api, fields, models


class FlspDeliveryAddress(models.Model):
    """
        Class_Name: FlspDeliveryAddress
        Model_Name: inherits the res.company model
        Purpose:    To help create flsp Delivery address
        Date:       Nov/16th/Monday/2020
        Updated:
        Author:     Sami Byaruhanga
    """
    _inherit = 'res.company'

    flsp_street = fields.Char(string='FLSP Street')
    flsp_street2 = fields.Char(string='FLSP Street 2')
    flsp_zip = fields.Char(string='FLSP ZIP', change_default=True)
    flsp_city = fields.Char(string='FLSP City')
    flsp_state_id = fields.Many2one("res.country.state", string='FLSP State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    flsp_country_id = fields.Many2one('res.country', string='FLSP Country', ondelete='restrict')
