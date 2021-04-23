# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FlspTktBoarding(models.Model):
    """
        Class_Name: FlspTktBoarding
        Model_Name: flspticketsystem.boarding
        Purpose:    To help in the creation of the tickets for employee boarding
        Date:       April.22nd.2021.Thursday
        Author:     Sami Byaruhanga
    """
    _name = 'flspticketsystem.boarding'
    _description = "Boarding"
    _rec_name = "name"

    name = fields.Char(string="Ticket Name", required=True)
    boarding = fields.Many2one('hr.plan', ondelete='cascade', string="Boarding")
    category_id = fields.Many2one('flspticketsystem.category', ondelete='cascade', default=5, string="Category")
    short_description = fields.Char(string="Short Description", size=80, required=True)
    detailed_description = fields.Text(string="Detailed Description", required=True)
