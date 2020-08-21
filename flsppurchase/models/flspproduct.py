# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class flsppurchaseproductprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_open_po_qty = fields.Float(compute='_compute_flsp_open_po_qty', string='Qty Open PO')

    def _compute_flsp_open_po_qty(self):
        if not self.purchase_ok:
            for product in self:
                product.flsp_open_po_qty = 0.0
        else:
            domain = [
                ('flsp_open_qty', '>', 0),
                ('product_id', 'in', self.ids)
            ]
            order_lines = self.env['purchase.order.line'].search(domain)
            for product in self:
                if not product.id:
                    product.flsp_open_po_qty = 0.0
                    continue
                for line in order_lines:
                    product.flsp_open_po_qty += line.flsp_open_qty
        if not self.flsp_open_po_qty:
            self.flsp_open_po_qty = 0

    def action_view_open_po(self):
        action = self.env.ref('flsppurchase.action_purchase_order_line_all').read()[0]
        action['domain'] = ['&', ('product_id', 'in', self.ids), ('flsp_open_qty', '>', 0)]
        return action


class flsppurchaseproducttmp(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    flsp_open_po_qty = fields.Float(compute='_compute_flsp_open_po_qty', string='Qty Open PO')

    def _compute_flsp_open_po_qty(self):
        if not self.purchase_ok:
            for template in self:
                template.flsp_open_po_qty = 0
        else:
            for template in self:
                template.flsp_open_po_qty = float_round(sum([p.flsp_open_po_qty for p in template.product_variant_ids]), precision_rounding=template.uom_id.rounding)

    def action_view_open_po(self):
        product_prd = self.env['product.product'].search([('product_tmpl_id', 'in', self.ids)])
        action = self.env.ref('flsppurchase.action_purchase_order_line_all').read()[0]
        action['domain'] = ['&', ('product_id', '=', product_prd.ids), ('flsp_open_qty', '>', 0)]
        return action
