# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class FlspCostDetProductProduct(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    def action_view_flsp_cost_detail(self):
        action = self.env.ref('flsp_cost_detail.flsp_cost_detail_action').read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        return action

class FlspCostDetProductTmpl(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    def action_view_flsp_cost_detail(self):
        action = self.env.ref('flsp_cost_detail.flsp_cost_detail_action').read()[0]
        action['domain'] = [('product_tmpl_id', '=', self.id)]
        return action
