# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class FlspSerialNumWizard(models.TransientModel):
    _name = 'flsp.serial.num.wizard'
    _description = "Wizard: Actions for Serial Numbers"

    order_id = fields.Many2one('flsp.serialnum', string='Reference')
    existing_lots = fields.Many2many('flsp.serialnumline', 'existing_lines', string='Existing Serial Num Lines')
    absent_lot_names = fields.Many2many('flsp.serialnumline', 'absent_lines', string='Absent Serial Num Lines')

    @api.model
    def default_get(self, fields):
        vals = super(FlspSerialNumWizard, self).default_get(fields)

        default_order_id = self.env.context.get('default_order_id')
        if default_order_id:
            order = self.env['flsp.serialnum'].search([('id', '=', default_order_id)])
            if order.exists():
                vals['order_id'] = order
                
                default_existing_lots = self.env.context.get('default_existing_lots')
                if default_existing_lots:
                    vals['existing_lots'] = self.env['flsp.serialnumline'].search([('order_id', '=', default_order_id), ('serial_num', 'in', default_existing_lots)])
                
                default_absent_lot_names = self.env.context.get('default_absent_lot_names')
                if default_absent_lot_names:
                    vals['absent_lot_names'] = order._write_absent_serialnum_lines(default_absent_lot_names)

        vals = self._convert_to_write(vals)
        return vals

    def action_continue_creation(self):
        if len(self.absent_lot_names) > 0:
            self.order_id.create_absent_serial_num(self.absent_lot_names.mapped('serial_num'))

        return {'type': 'ir.actions.act_window_close'} 
