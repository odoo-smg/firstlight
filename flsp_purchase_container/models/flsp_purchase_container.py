# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, time
import logging

_logger = logging.getLogger(__name__)
#######################################################
# Class..: Container
# Author.: Alexandre Sousa
# Date...: March/22th/Tuesday/2022
# Purpose: To manage delivery dates of oversea purchase
#######################################################
class Container(models.Model):

    _name = 'flsp.purchase.container'
    _description = "Container"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, help='Please provide the container description or code')
    expected_date = fields.Date(string="Expected Date", required=True, help='Expected arrival date')
    responsible = fields.Many2one('res.users', string="Responsible", required=True, index=True,
        default=lambda self: self.env.user)
    comments = fields.Text(string="Comments")
    status = fields.Selection([('overseas', 'Overseas'), ('at_sea', 'At Sea'),
                               ('in_canada', 'In Canada'), ('received', 'Received')],
                                default='overseas', eval=True)
    received_date = fields.Date(string="Received Date", readonly=True)

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments',
        help='Add any attachments that belongs to the container')

    container_lines = fields.One2many(comodel_name='flsp.purchase.container.line', inverse_name='container_id', string="Items")

    def action_picking_move_tree(self):
        action = self.env.ref('stock.stock_move_action').read()[0]
        action['views'] = [
            (self.env.ref('stock.view_picking_move_tree').id, 'tree'),
        ]
        action['context'] = self.env.context
        action['domain'] = [('picking_id', 'in', self.container_lines.picking_id.ids)]
        return action

    def container_receive(self):
        for line in self.container_lines:
            self.receive_receipt(line.picking_id)
        self.status = 'received'

    def receive_receipt(self, picking_id):
        if not picking_id:
            return
        if picking_id.state == 'done':
            return
        for move in picking_id.move_ids_without_package:
            self.create_stock_move_line(move)
        picking_id.button_validate()

    def create_stock_move_line(self, move_id):
        if not move_id:
            return

        if move_id.product_id.tracking == 'none':
            lot_serial_id = False
        elif move_id.product_id.tracking == 'lot':
            lot_serial_id = self.create_lot(move_id.product_id)
        else: ## serial - do not receive serial
            return

        stock_move_line = self.env['stock.move.line'].create({
            'product_id': move_id.product_id.id,
            'product_uom_id': move_id.product_uom.id,
            'qty_done': move_id.product_uom_qty,
            'picking_id': move_id.picking_id.id,
            'reference': move_id.picking_id.name,
            'move_id': move_id.id,
            'location_id': move_id.location_id.id,
            'location_dest_id': move_id.location_dest_id.id,
            'lot_id': lot_serial_id,
        })

    def create_lot(self, product_id):
        if product_id:
            part_init = product_id.default_code[0:6]
            self._cr.execute(
                "select max(name) as code from stock_production_lot where name like '" + part_init + "%' and length(name) = 13")
            retvalue = self._cr.fetchall()
            returned_registre = retvalue[0]
            nextseqnum = self._get_next_seqnum(returned_registre[0])
            nextlotnum = part_init
            nextlotnum = nextlotnum + "_"
            nextlotnum = nextlotnum + nextseqnum

            lot = self.env['stock.production.lot'].create({
                'name': nextlotnum,
                'product_id': product_id.id,
                'company_id': self.env.company.id})
            return lot.id
        else:
            return False

    def _get_next_seqnum(self, currpartnum):
        if not currpartnum:
            retvalue = '000001'
        else:
            retvalue = ('00000' + str(int(currpartnum[-5:]) + 1))[-6:]

        return retvalue


    def purchase_wizard(self):
        action = self.env.ref('flsp_purchase_container.launch_flsp_purchase_container_po_wiz').read()[0]
        return action

    @api.depends('expected_date')
    def write(self, values):
        res = super().write(values)
        if "status" in values:
            self.message_post(body='Status : ' + dict(self._fields['status'].selection).get(self.status))
        if "expected_date" in values:
            if self.container_lines:
                for line in self.container_lines:
                    line.picking_id.scheduled_date = datetime.combine(self.expected_date, time(12, 0, 0))
                    if line.picking_id.move_ids_without_package:
                        for move in line.picking_id.move_ids_without_package:
                            move.date_expected = datetime.combine(self.expected_date, time(12, 0, 0))

            self.message_post(body='Expected date changed to : ' + str(self.expected_date))
        return res

class ContainerLine(models.Model):

    _name = 'flsp.purchase.container.line'
    _description = "Container Line"

    container_id = fields.Many2one('flsp.purchase.container', required=True)
    purchase_id = fields.Many2one('purchase.order', string='PO', required=True)
    picking_id = fields.Many2one('stock.picking', string='Receipt', required=True)
