# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class FlspStockContainerWizard(models.TransientModel):
    _name = 'flsp.purchase.container.stock.picking.wiz'
    _description = "Wizard: Include this Receipt in a Container"

    container_id = fields.Many2one('flsp.purchase.container', required=True, domain="[('status', '=', 'overseas')]")
    picking_id = fields.Many2one('stock.picking', string='Receipt', required=True)

    @api.model
    def default_get(self, fields):
        res = super(FlspStockContainerWizard, self).default_get(fields)
        picking_id = self.env.context.get('active_id')
        if picking_id:
            stock_picking = self.env['stock.picking'].browse(picking_id)
        if stock_picking.exists():
            if 'picking_id' in fields:
                res['picking_id'] = stock_picking.id
                res['container_id'] = stock_picking.flsp_container_id.id

        res = self._convert_to_write(res)
        return res

    def flsp_confirm(self):
        print('confirmed')
        self.ensure_one()
        if self.picking_id.flsp_purchase_id:
            print('po ok: contatainer:')
            print(self.container_id)
            return self.env['flsp.purchase.container.line'].create({
                'container_id': self.container_id.id,
                'purchase_id': self.picking_id.flsp_purchase_id.id,
                'picking_id': self.picking_id.id,
            })
        else:
            purchase_id = False
            print("missing po, container: ")
            print(self.container_id)

            if self.picking_id.move_ids_without_package:
                for move in self.picking_id.move_ids_without_package:
                    if move.purchase_line_id:
                        purchase_id = move.purchase_line_id.order_id
            print('-->PO:')
            print(purchase_id)
            if purchase_id:
                print("found po, container: ")
                print(self.container_id)
                self.picking_id.flsp_purchase_id = purchase_id
                return self.env['flsp.purchase.container.line'].create({
                    'container_id': self.container_id.id,
                    'purchase_id': self.picking_id.flsp_purchase_id.id,
                    'picking_id': self.picking_id.id,
                })


