# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Flspwipwizard(models.TransientModel):
    _name = 'flsp_wip_transfer.wizard'
    _description = "Wizard: Recalculate Demands"

    consider_days_ahead = fields.Integer(String="Days ahead", default=7, help="Days ahead.")

    def flsp_report(self):
        self.ensure_one()
        action = self.env.ref('flsp_wip_transfer.flsp_wip_view_action').read()[0]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action

    def flsp_recalc(self):
        self.env['flsp.wip.transfer']._flsp_calc_demands(self.consider_days_ahead)
        #action = self.env.ref('flsp_wip_transfer.flsp_wip_transfer_action').read()[0]
        action = self.env.ref('flsp_wip_transfer.flsp_wip_view_action').read()[0]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action
