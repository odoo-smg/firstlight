# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class WipResponsible(models.Model):
    """
        Class_Name: WIP Responsible
        Model_Name: flsp_mrp_wip.flsp_wip_responsible
        Purpose:    To manage the WIP Transfer by location
        Date:       July/9th/2021
        Author:     Alexandre Sousa
    """
    _name = 'flsp.wip.responsible'
    _description = "WIP Responsible"

    id = fields.Integer(index=True)
    sequence = fields.Integer(string="Sequence")
    responsible = fields.Many2one('res.users', string="Responsible", required=True, index=True,
         help='Select the responsible for the WIP Transfer')
    parent_location = fields.Many2one('stock.location', string="Parent Location", help='Select the parent location for WIP Transfer')
    text_location = fields.Char(string="Location Name %", help='Inform the beginning of the location name')
