# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class FlspCostScenarioWiz(models.TransientModel):
    _name = 'flsp.cost.scenario.wiz'
    _description = "Wizard: Recalculate Cost Scenarios"

    @api.model
    def _flsp_default_currency(self):
        return self.env['res.currency'].search([('name', '=', 'USD')], limit=1)

    currency_id = fields.Many2one("res.currency", string="Currency", help="Currency of the report", required=True,
                                  domain="[('name', 'in', ['USD', 'CAD'])]")

    @api.model
    def default_get(self, fields):
        res = super(FlspCostScenarioWiz, self).default_get(fields)
        currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        print(currency)
        if currency.exists():
            print(currency.name)
            if 'currency_id' in fields:
                res['currency_id'] = currency.id
        res = self._convert_to_write(res)
        return res

    def flsp_report(self):
        usd_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id
        if self.currency_id.id == usd_id:
            action = self.env.ref('flsp-product.flsp_cost_scenario_usd_action').read()[0]
        else:
            action = self.env.ref('flsp-product.flsp_cost_scenario_action').read()[0]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action

    def flsp_recalc(self):
        self.env['product.template'].flspCostUpdate()
        usd_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id
        if self.currency_id.id == usd_id:
            action = self.env.ref('flsp-product.flsp_cost_scenario_usd_action').read()[0]
        else:
            action = self.env.ref('flsp-product.flsp_cost_scenario_action').read()[0]

        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action
