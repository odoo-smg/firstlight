# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class flspmrpwipproduction(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    #flsp_wip_transfer_ids = fields.One2many('stock.picking', inverse_name='flsp_mo_wip_id', string="Transfer Created: ")
    flsp_wip_transfer_ids = fields.One2many('stock.picking', string="Transfer Created: ")

    def button_flsp_mrp_wip(self):
        """
            Purpose: To transfer components from Stock to WIP
        """
        view_id = self.env.ref('flsp_mrp_wip.flsp_mrp_wip_wiz_form_view').id
        return {
            'name': 'WIP Transfer',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flsp.mrp.wip.wiz',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_mo_id': self.id,
                'show_sublevels': False,
                'wip_id': False,
            }
        }
