# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Type(models.Model):
    """
        Class_Name: Ticket
        Model_Name: flspticketsystem.ticket
        Purpose:    To help in the creation of the tickets type specification
        Date:       sept/16th/Wednesday/2020
        Author:     Sami Byaruhanga
    """
    _name = 'flspticketsystem.type'
    _description = "Type"

    name = fields.Char(string="Request type", required=True)
    description = fields.Text()
