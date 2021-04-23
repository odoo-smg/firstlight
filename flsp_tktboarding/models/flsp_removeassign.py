# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FlspTktRemoveAssign(models.Model):
    """
        class_name: FlspTktRemoveAssign
        model_name: inherits the flspticketsytem.ticket
        Purpose:    To help remove responsible from ticket
        Date:       April/23/2021/F
        Author:     Sami Byaruhanga
    """
    _inherit = "flspticketsystem.ticket"

    def button_remove_assign(self):
        """
            Purpose: To remove assigned from the ticket and move to open state
        """
        
        for record in self:
            if record.status == 'inprogress':
                self.write({'status': 'open'})
                self.responsible = None


