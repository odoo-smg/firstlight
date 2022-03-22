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

