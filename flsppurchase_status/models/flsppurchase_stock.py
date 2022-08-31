# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class FlsppurchaseStockPicking(models.Model):
    _inherit = 'stock.picking'

    flsp_purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    flsp_show_purchaseline = fields.Boolean(string='Show PO line', compute="_compute_flsp_show_purchaseline")

    @api.depends('flsp_purchase_id')
    def _compute_flsp_show_purchaseline(self):
        for each in self:
            if each.flsp_purchase_id:
                each.flsp_show_purchaseline = True
            else:
                each.flsp_show_purchaseline = False

    @api.model
    def default_get(self, fields):
        res = super(FlsppurchaseStockPicking, self).default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'purchase.order':
            order = self.env['purchase.order'].browse(self.env.context.get('active_id'))
            if order.exists():
                res['flsp_purchase_id'] = order.id
        return res


class FlsppurchaseStockMove(models.Model):
    _inherit = 'stock.move'

    flsp_show_purchaseline = fields.Boolean(string='Show PO line', compute="_compute_flsp_show_purchaseline")

    @api.depends('picking_id.flsp_show_purchaseline')
    def _compute_flsp_show_purchaseline(self):
        for each in self:
            each.flsp_show_purchaseline = each.picking_id.flsp_show_purchaseline
