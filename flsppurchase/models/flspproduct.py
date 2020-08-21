# -*- coding: utf-8 -*-

from odoo import fields, models, api


class flsppurchaseproductprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    def action_product_open_po_report(self):
        action = self.env.ref('flsppurchase.report_open_po_action_product').read()[0]
        action['domain'] = [
            ('product_id', '=', self.id), ('qty_received', '=', 0),
        ]
        return action
