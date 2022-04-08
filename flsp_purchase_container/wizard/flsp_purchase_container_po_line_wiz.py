# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, time
import logging

_logger = logging.getLogger(__name__)


class FlspPoLineWizard(models.TransientModel):
    _name = 'flsp.purchase.container.po.line.wiz'
    _description = "Wizard: Include items of PO line into Container"

    container_id = fields.Many2one('flsp.purchase.container', required=True, domain="[('status', '=', 'overseas')]")
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    purchase_line_ids = fields.One2many('flsp.purchase.container.po.line.line.wiz', 'flsp_purchase_container_po_line_wiz_id', string='Purchase lines')
    receipts_handle = fields.Selection([('one','Create a unique receipt for all remaining quantity in the PO'),
                                        ('date','Create one receipt for each scheduled date of the items with remaining quantity in the PO')]
                                       , string="Remaining Qty", default='one')
    user_msg = fields.Char('Message Fail')
    okay_msg = fields.Char('Message Pass')

    @api.model
    def default_get(self, fields):
        res = super(FlspPoLineWizard, self).default_get(fields)
        container_id = self.env.context.get('container_id')
        purchase_id = self.env.context.get('purchase_id')
        user_msg = self.env.context.get('user_msg')
        okay_msg = self.env.context.get('okay_msg')
        line_contex = self.env.context.get('line_contex')
        if okay_msg:
            if 'okay_msg' in fields:
                res['okay_msg'] = okay_msg
        else:
            res['okay_msg'] = False
        if user_msg:
            if 'user_msg' in fields:
                res['user_msg'] = user_msg
        if purchase_id:
            purchase = self.env['purchase.order'].browse(purchase_id)
        if container_id:
            container = self.env['flsp.purchase.container'].browse(container_id)
        if container.exists():
            if 'container_id' in fields:
                res['container_id'] = container.id
        if purchase.exists():
            if 'purchase_id' in fields:
                res['purchase_id'] = purchase.id
            if line_contex:
                line_list = line_contex
            else:
                line_list = []
                for po_line in [l for l in purchase.order_line]:
                    if po_line.product_id:
                        line_list.append([0, 0, {
                            'flsp_purchase_container_po_line_wiz_id': purchase.id,
                            'sequence': po_line.sequence,
                            'product_template_id': po_line.product_id.product_tmpl_id.id,
                            'product_qty': po_line.product_uom_qty,
                            'product_uom': po_line.product_id.product_tmpl_id.uom_id.id,
                            'name': po_line.name,
                            'purchase_order_line_id': po_line.id,
                            'order_id': po_line.order_id.id,
                            'qty_received': po_line.qty_received,
                            'qty_other_container': self.find_other_container(po_line, False, container),
                            'date_planned': po_line.date_planned,
                        }])
            res['purchase_line_ids'] = line_list


        res = self._convert_to_write(res)
        return res

    def find_other_container(self, po_line, consider_current=False, container=False):
        ret = 0
        moves = self.env['stock.move'].search(['&', ('purchase_line_id', '=', po_line.id), ('state', 'not in', ['done', 'cancel'])])
        for move in moves:
            if move.picking_id.flsp_container_id:
                if consider_current:
                    ret += move.product_uom_qty
                else:
                    if container:
                        container_id = container.id
                    else:
                        container_id = self.container_id.id
                    if move.picking_id.flsp_container_id.id != container_id:
                        ret += move.product_uom_qty
        return ret

    def flsp_generate(self):
        self.delete_previous_receits()
        receitp = self.create_new_receits()
        if receitp:
            self.create_new_line(receitp)
        self.create_new_receit_from_po_line()

    def create_new_line(self, receitp):
        self.env['flsp.purchase.container.line'].create({
                    'container_id': self.container_id.id,
                    'purchase_id': self.purchase_id.id,
                    'picking_id': receitp.id,
                })

    def create_new_receit_from_po_line(self):
        qty = 0
        for line in self.purchase_id.order_line:
            other_container = self.find_other_container(line, True)
            if line.product_uom_qty - (line.qty_received + other_container) > 0:
                qty += line.product_uom_qty - (line.qty_received + other_container)

        if qty <= 0:
            return

        stock_picking = False
        picking_type_id = self.env['stock.picking.type'].search([('sequence_code', '=', 'IN')], limit=1)
        partner_location = self.env['stock.location'].search([('usage', '=', 'supplier')], limit=1)

        #container_id        purchase_id       purchase_line_ids        receipts_handle
        purchase_lines = self.env['purchase.order.line'].search(['&', ('order_id', '=', self.purchase_id.id), ('product_qty', '>', 0)]).sorted(lambda r: r.date_planned)

        if purchase_lines:
            if self.receipts_handle == 'one':
                stock_picking = self.create_stock_picking()
                if stock_picking:
                    for line in purchase_lines:
                        other_container = self.find_other_container(line, True)
                        qty = 0
                        if line.product_uom_qty - (line.qty_received + other_container) > 0:
                            qty += line.product_uom_qty - (line.qty_received + other_container)

                        if qty > 0:
                            stock_move = self.env['stock.move'].create({
                                'name': line.name,
                                'product_id': line.product_id.id,
                                'product_uom': line.product_id.uom_id.id,
                                'product_uom_qty': qty,
                                'picking_id': stock_picking.id,
                                'date_expected': line.date_planned,
                                'purchase_line_id': line.id,
                                'origin': self.purchase_id.name,
                                'description_picking': line.name,
                                'location_id': partner_location.id,
                                'location_dest_id': picking_type_id.default_location_dest_id.id,
                            })
                    stock_picking.action_confirm()
            else:
                stock_picking = self.create_stock_picking()
                current_date = False
                if stock_picking:
                    for line in purchase_lines:
                        if not current_date:
                            current_date = line.date_planned.date()

                        other_container = self.find_other_container(line, True)
                        qty = 0
                        if line.product_uom_qty - (line.qty_received + other_container) > 0:
                            qty += line.product_uom_qty - (line.qty_received + other_container)

                        if qty > 0:
                            if current_date != line.date_planned.date():
                                stock_picking.action_confirm()
                                stock_picking = self.create_stock_picking()
                                current_date = line.date_planned.date()

                            stock_move = self.env['stock.move'].create({
                                'name': line.name,
                                'product_id': line.product_id.id,
                                'product_uom': line.product_id.uom_id.id,
                                'product_uom_qty': qty,
                                'picking_id': stock_picking.id,
                                'date_expected': line.date_planned,
                                'purchase_line_id': line.id,
                                'origin': self.purchase_id.name,
                                'description_picking': line.name,
                                'location_id': partner_location.id,
                                'location_dest_id': picking_type_id.default_location_dest_id.id,
                            })
                    stock_picking.action_confirm()

        return stock_picking

    def create_stock_picking(self):
        stock_picking = False
        picking_type_id = self.env['stock.picking.type'].search([('sequence_code', '=', 'IN')], limit=1)
        partner_location = self.env['stock.location'].search([('usage', '=', 'supplier')], limit=1)

        create_val = {
            'origin': self.purchase_id.name,
            'partner_id': self.purchase_id.partner_id.id,
            'picking_type_id': picking_type_id.id,
            'location_id': partner_location.id,
            'company_id': self.env.company.id,
            'location_dest_id': picking_type_id.default_location_dest_id.id,
            'flsp_purchase_id': self.purchase_id.id,
            'scheduled_date': datetime.combine(self.container_id.expected_date, time(12, 0, 0)),
        }
        stock_picking = self.env['stock.picking'].create(create_val)

        return stock_picking


    def create_new_receits(self):
        # Create Receipt for the container
        stock_picking = False
        picking_type_id = self.env['stock.picking.type'].search([('sequence_code', '=', 'IN')], limit=1)
        partner_location = self.env['stock.location'].search([('usage', '=', 'supplier')], limit=1)

        '''
        # commented to delete later
        create_val = {
            'origin': self.purchase_id.name,
            'partner_id': self.purchase_id.partner_id.id,
            'picking_type_id': picking_type_id.id,
            'location_id': partner_location.id,
            'company_id': self.env.company.id,
            #'location_id': picking_type_id.default_location_src_id.id,
            'location_dest_id': picking_type_id.default_location_dest_id.id,
            'flsp_purchase_id': self.purchase_id.id,
            'scheduled_date': datetime.combine(self.container_id.expected_date, time(12, 0, 0)),
        }
        stock_picking = self.env['stock.picking'].create(create_val)
        '''
        stock_picking = self.create_stock_picking()

        if stock_picking:
            for line in self.purchase_line_ids:
                prod = self.env['product.product'].search([('product_tmpl_id', '=', line.product_template_id.id)])
                stock_move = self.env['stock.move'].create({
                    'name': line.name,
                    'product_id': prod.id,
                    'product_uom': prod.uom_id.id,
                    'product_uom_qty': line.qty_container,
                    'picking_id': stock_picking.id,
                    'origin': line.order_id.name,
                    'description_picking': line.name,
                    'date_expected': datetime.combine(self.container_id.expected_date, time(12, 0, 0)),
                    'purchase_line_id': line.purchase_order_line_id.id,
                    'location_id': partner_location.id,
                    'location_dest_id': picking_type_id.default_location_dest_id.id,
                })
            stock_picking.action_confirm()

        return stock_picking




    def delete_previous_receits(self):
        if self.purchase_id.order_line:
            moves = self.env['stock.move'].search([('purchase_line_id', 'in', self.purchase_id.order_line.ids)])
            for move in moves:
                if move.picking_id.flsp_container_id:
                    if move.picking_id.flsp_container_id != self.container_id:
                        continue
                if move.picking_id.state not in ('done','cancel'):
                    move.picking_id.action_cancel()
                    if move.picking_id.flsp_container_id:
                        # delete from container
                        container_line = self.env['flsp.purchase.container.line'].search([('picking_id', '=', move.picking_id.id)])
                        if container_line:
                            container_line.unlink()

    def flsp_confirm(self):

        user_msg = False
        okay_msg = False
        date_line = False

        # Check Quantity
        total_qty = 0
        for line in self.purchase_line_ids:
            if line.qty_container:
                if (line.qty_container > line.product_qty - line.qty_received):
                    user_msg = 'Please, review product: '+line.product_template_id.default_code+' container quantity is bigger than open (Quantity-Received).'
                total_qty += line.qty_container
                if not date_line:
                    date_line = line.date_planned.date()
                else:
                    if date_line != line.date_planned.date():
                        user_msg = 'Please, select parts from the same scheduled date.'
        if total_qty == 0:
            user_msg = 'Please, inform the quantity of each item that you want to include in the container.'

        if not user_msg:
            # Pass
            okay_msg = "A new receipt will be created for the lines below. Please, review it and confirm it."

        action = self.env.ref('flsp_purchase_container.launch_flsp_purchase_container_po_line_wiz').read()[0]
        if self.purchase_id:
            line_contex = []
            for line in self.purchase_line_ids:
                if okay_msg:
                    if line.qty_container <= 0:
                        continue
                line_contex.append([0, 0, {
                    'flsp_purchase_container_po_line_wiz_id': line.id,
                    'sequence': line.sequence,
                    'product_template_id': line.product_template_id.id,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom.id,
                    'purchase_order_line_id': line.purchase_order_line_id.id,
                    'name': line.name,
                    'order_id': line.order_id.id,
                    'qty_received': line.qty_received,
                    'qty_other_container': line.qty_other_container,
                    'qty_container': line.qty_container,
                    'date_planned': line.date_planned,
                }])
            action_context = {'purchase_id': self.purchase_id.id,
                              'container_id': self.container_id.id,
                              'line_contex': line_contex,
                              'user_msg': user_msg,
                              'okay_msg': okay_msg}
            action['context'] = action_context

        return action


class FlspPoLineLineWizard(models.TransientModel):
    """Purchase lines"""
    _name = 'flsp.purchase.container.po.line.line.wiz'
    _description = 'Select Line from PO'

    flsp_purchase_container_po_line_wiz_id = fields.Many2one('flsp.purchase.container.po.line.wiz')
    purchase_order_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line')
    order_id = fields.Many2one('purchase.order', string='Purchase Order')
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Name')
    product_template_id = fields.Many2one('product.template', string='Product Template')
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', default=1.0)
    qty_received = fields.Float(string='Received', digits='Product Unit of Measure', default=1.0)
    qty_other_container = fields.Float(string='Other Container', digits='Product Unit of Measure')
    qty_container = fields.Float(string='This Container', digits='Product Unit of Measure')
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    date_planned = fields.Datetime('Scheduled Date')
