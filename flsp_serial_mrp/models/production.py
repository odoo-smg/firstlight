# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class flspserialproduction(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    flsp_serial_mrp = fields.Boolean('Lot/Serial on MO', related='product_id.flsp_serial_mrp')

    def flsp_button_serial_mrp_two(self):
        action = self.env.ref('flsp_serial_mrp.launch_flsp_serial_mrp_wiz_two').read()[0]
        return action


    def flsp_button_serial_mrp(self):
        """
            Purpose: To show product lot entries for the MO in a wizard
        """
        action = self.env.ref('flsp_serial_mrp.launch_flsp_serial_mrp_wiz').read()[0]
        return action


    def button_mark_done(self):
        if self.flsp_serial_mrp:
            action = self.env.ref('flsp_serial_mrp.launch_flsp_serial_alert_wiz').read()[0]
            serial_mrp = self.env['flsp.serial.mrp.two'].search([('mo_id', '=', self.id)])
            is_completed = True
            count_lots = 0
            for line in serial_mrp:
                if len(line.component_lot_ids.ids) <= 0:
                    is_completed = False
                count_lots = count_lots + len(line.component_lot_ids.ids)
            if not is_completed or count_lots == 0:
                return action

        return super(flspserialproduction, self).button_mark_done()

