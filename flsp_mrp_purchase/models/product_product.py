# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class mrppruchaseprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    def action_view_mrp_purchase(self):
        action = self.env.ref('flsp_mrp_purchase.flsp_mrp_purchase_line_action').read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        return action

class flsppurchaseproductprdtmpl(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    def action_view_mrp_purchase(self):
        action = self.env.ref('flsp_mrp_purchase.flsp_mrp_purchase_line_action').read()[0]
        action['domain'] = [('product_tmpl_id', '=', self.id)]
        return action
