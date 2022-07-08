# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class pruchasemrpprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    def action_view_purchase_mrp(self):
        admin = self.env.ref('base.user_admin')
        purchase_mrp_id = self.env['flsp.purchase.mrp'].search([('state', '=', 'done')], limit=1, order='id DESC')

        action = self.env.ref('flsp_purchase_mrp.flsp_purchase_mrp_line_action').read()[0]
        action['domain'] = ['&', ('product_id', '=', self.id), ('purchase_mrp_id', '=', purchase_mrp_id.id)]
        return action

class purchasepmrprdtmpl(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    def action_view_purchase_mrp(self):
        admin = self.env.ref('base.user_admin')
        purchase_mrp_id = self.env['flsp.purchase.mrp'].search([('state', '=', 'done')], limit=1, order='id DESC')
        action = self.env.ref('flsp_purchase_mrp.flsp_purchase_mrp_line_action').read()[0]
        action['domain'] = ['&', ('product_tmpl_id', '=', self.id), ('purchase_mrp_id', '=', purchase_mrp_id.id)]
        return action
