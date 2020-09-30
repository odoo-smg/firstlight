# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Package(models.TransientModel):
    """
        Class_Name: Package
        Model_Name: flspticketsystem.assign
        Purpose:    To create an assign model used in the wizard to assign responsible
        Date:       sept/24th/Thursday/2020
        Author:     Sami Byaruhanga
    """

    _name = 'flspstock.package'
    _description = "Package wizard"

    # Used in view form
    order_id = fields.Many2one('stock.picking', default=True)    # getting the order_id
    flsp_packingdesc = fields.Text(string="Packing Description")

    # Methods
    def confirm(self):
        """
            Purpose: To send an email with the package info entered and update package info
        """
        self.ensure_one()
        self.order_id.write({'flsp_packingdesc': self.flsp_packingdesc, })
        self.env['flspautoemails.bpmemails'].send_email(self, 'SO0009')
