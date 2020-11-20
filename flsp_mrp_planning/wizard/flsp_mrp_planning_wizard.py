# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class FlspMrpPlanningWizard(models.TransientModel):
    _name = 'flsp_mrp_planning.wizard'
    _description = "Wizard: Recalculate Planning"

    calculate_sub_levels = fields.Boolean(String="Sub-Levels", default=0, help="Calculate sub-levels of BOM.")
    standard_lead_time = fields.Integer(String="Lead time", default=14, help="Standard Lead time.")
    standard_queue_time = fields.Integer(String="Lead time", default=1, help="Standard queue time.")

    @api.model
    def default_get(self, fields):
        res = super(FlspMrpPlanningWizard, self).default_get(fields)
        return res

    def flsp_report(self):
        self.ensure_one()

        action = self.env.ref('flsp_mrp_planning.flsp_mrp_planning_line_action').read()[0]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action

    def flsp_recalc(self):
        self.env['flsp.mrp.planning.line']._flsp_calc_planning(self.calculate_sub_levels, self.standard_lead_time, self.standard_queue_time)

        #product = self.env['product.product'].search([], limit=1)
        #product._flsp_calc_suggested_qty()
        #action = self.env.ref('flsppurchase.purchase_suggestion_action').read()[0]
        action = self.env.ref('flsp_mrp_planning.flsp_mrp_planning_line_action').read()[0]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action
