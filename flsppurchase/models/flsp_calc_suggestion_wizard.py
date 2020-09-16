# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Suggestionwizard(models.TransientModel):
    _name = 'flsppurchase.suggestionwizard'
    _description = "Wizard: Recalculate Suggestion"

    @api.model
    def default_get(self, fields):
        res = super(Suggestionwizard, self).default_get(fields)
        return res

    def flsp_report(self):
        self.ensure_one()
        action = self.env.ref('flsppurchase.purchase_suggestion_action').read()[0]
        return action

    def flsp_recalc(self):
        product = self.env['product.product'].search([], limit=1)
        product._flsp_calc_suggested_qty()
