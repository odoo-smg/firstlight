# -*- coding: utf-8 -*-
import os

from odoo import models, fields, api
# import logging

# _logger = logging.getLogger(__name__)
# def _moduleName():
#     path = os.path.dirname(__file__)
#     return os.path.basename(os.path.dirname(path))
# openerpModule = _moduleName()

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
                        Returns the view
        """
        self.ensure_one()
        self.env['flsp.bom.availability'].create({'bom': self.bom.id})
        # self.env['flsp.comparebom'].create({'bom': self.bom.id})
        res = self.env['flsp.bom.availability.view'].search([], limit=1).id #returns number 1
        view = self.env.ref('flsp_bom_availability.flsp_bom_availability_view_form').id

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view,
            'res_model': 'flsp.bom.availability.view',
            'domain': [],
            # 'target': 'new',  # to clear the breadcrumbs
            'target': 'main',  # to clear the breadcrumbs
            'res_id': res,      #very useful since it helps show which form to open, it can be any form i want
        }
