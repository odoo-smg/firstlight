# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class flspserialproduction(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    def flsp_button_serial_mrp_two(self):
        action = self.env.ref('flsp_serial_mrp.launch_flsp_serial_mrp_wiz_two').read()[0]
        return action


    def flsp_button_serial_mrp(self):
        print("calling it************************")
        """
            Purpose: To show product lot entries for the MO in a wizard
        """

        action = self.env.ref('flsp_serial_mrp.launch_flsp_serial_mrp_wiz').read()[0]
        return action

        view_id = self.env.ref('flsp_serial_mrp.launch_flsp_serial_mrp_wiz').id
        return {
            'name': 'Product Serial/Lot Entries',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flsp_serial_mrp.wizard',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_mo_id': self.id,
            }
        }
