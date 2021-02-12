# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class FlspMrpPlanningWizard(models.TransientModel):
    _name = 'flsp_mrp_planning.wizard'
    _description = "Wizard: Recalculate Planning"

    calculate_sub_levels = fields.Boolean(String="Sub-Levels", default=0, help="Calculate sub-levels of BOM.")
    standard_lead_time = fields.Integer(String="Lead time", default=14, help="Standard Lead time.")
    standard_i_lead_time = fields.Integer(String="Lead time Indirect", default=1, help="Standard Indirect Lead time.")
    standard_queue_time = fields.Integer(String="Lead time", default=1, help="Standard queue time.")
    orders_to_confirm = fields.Boolean(String="Orders to confirm", default=False)
    consider_drafts = fields.Boolean(String="Consider Draft MOs", default=True)
    consider_wip = fields.Boolean(String="Consider WIP balance", default=False)
    consider_forecast = fields.Boolean(String="Consider Forecast", default=False)

    @api.model
    def default_get(self, fields):
        res = super(FlspMrpPlanningWizard, self).default_get(fields)
        mrp_draft = self.env['mrp.production'].search([('state', 'in', ['draft'])])
        if mrp_draft.exists():
            if 'orders_to_confirm' in fields:
                res['orders_to_confirm'] = True

        res = self._convert_to_write(res)
        return res

    def flsp_report(self):
        self.ensure_one()

        action = self.env.ref('flsp_mrp_planning.flsp_mrp_planning_line_action').read()[0]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action

    def flsp_recalc(self):
        #self.env['flsp.mrp.planning.line']._flsp_calc_planning(self.calculate_sub_levels, self.standard_lead_time, self.standard_queue_time, self.standard_i_lead_time, self.consider_drafts)
        self.env['flsp.mrp.planning.line']._flsp_calc_planning(self.standard_lead_time, self.standard_queue_time, self.standard_i_lead_time, self.consider_drafts, self.consider_wip, self.consider_forecast)

        #product = self.env['product.product'].search([], limit=1)
        #product._flsp_calc_suggested_qty()
        #action = self.env.ref('flsppurchase.purchase_suggestion_action').read()[0]
        action = self.env.ref('flsp_mrp_planning.flsp_mrp_planning_line_action').read()[0]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action

    def flsp_confirm_mo(self):
        print('confirming')
        mrp_draft = self.env['mrp.production'].search([('state', 'in', ['draft'])])
        for mo in mrp_draft:
            print('confirming mo: '+mo.name)
            mo.action_confirm()
        self.orders_to_confirm = False
        return {
            "type": "ir.actions.act_window",
            "name": "MRP Planning",
            "view_mode": "form",
            "res_model": "flsp_mrp_planning.wizard",
            "view_id": self.env.ref(
                "flsp_mrp_planning.flsp_mrp_planning_wizard_form_view"
            ).id,
            "target": "new",
            "res_id": self.id,
        }
