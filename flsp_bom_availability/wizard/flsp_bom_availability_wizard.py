# -*- coding: utf-8 -*-
from odoo import models, fields

class FlspBomAvailabilityWizard(models.TransientModel):
    """
        Class_Name: FlspBomAvailabilityWizard
        Model_Name: flsp.bom.availability.wizard
        Purpose:    To ask the user what BOM to show
        Date:       March/2nd/2021/T
        Author:     Sami Byaruhanga
    """
    _name = 'flsp.bom.availability.wizard'
    _description = "FLSP BoM Availability Wizard"

    bom = fields.Many2one('mrp.bom', string='BOM', required=True, ondelete='cascade')

    def display_availability(self):
        """
            Purpose:    Save bom,
                        Then use that in def init to get information for bom
                        Returns the tree view action
        """
        self.ensure_one()
        self.env['flsp.bom.availability'].create({'bom': self.bom.id})
        action = self.env.ref('flsp_bom_availability.flsp_bom_availability_line_action').read()[0]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action

