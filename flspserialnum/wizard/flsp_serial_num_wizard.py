# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class FlspSerialNumWizard(models.TransientModel):
    _name = 'flsp.serial.num.wizard'
    _description = "Wizard: Actions for Serial Numbers"

    order_id = fields.Many2one('flsp.serialnum', string='Reference')
    existing_lots = fields.Many2many('flsp.serialnumline', 'existing_lines', string='Existing Serial Num Lines')
    absent_lots = fields.Many2many('flsp.serialnumline', 'absent_lines', string='Absent Serial Num Lines')
    extra_lots = fields.Many2many('flsp.serialnumline', 'extra_lines', string='Extra Serial Num Lines')

    @api.model
    def default_get(self, fields):
        vals = super(FlspSerialNumWizard, self).default_get(fields)

        default_order_id = self.env.context.get('default_order_id')
        if default_order_id:
            order = self.env['flsp.serialnum'].search([('id', '=', default_order_id)])
            if order.exists():
                vals['order_id'] = order
                
                default_existing_lot_names = self.env.context.get('default_existing_lot_names')
                if default_existing_lot_names:
                    vals['existing_lots'] = self.env['flsp.serialnumline'].search([('order_id', '=', default_order_id), ('serial_num', 'in', default_existing_lot_names)])
                
                default_absent_lot_names = self.env.context.get('default_absent_lot_names')
                if default_absent_lot_names:
                    vals['absent_lots'] = order._write_absent_serialnum_lines(default_absent_lot_names)
                    
                default_extra_lot_names = self.env.context.get('default_extra_lot_names')
                vals['extra_lots'] = self.env['flsp.serialnumline'].search([('order_id', '=', default_order_id), ('serial_num', 'in', default_extra_lot_names)])

        vals = self._convert_to_write(vals)
        return vals

    def action_button_continue_creation(self):
        if len(self.absent_lots) > 0:
            self.order_id.create_absent_serial_num(self.absent_lots.mapped('serial_num'))
            
        if len(self.extra_lots) > 0:
            self.order_id.unlink_serial_num(self.extra_lots.mapped('serial_num'))
            self.extra_lots.unlink()

        return {'type': 'ir.actions.act_window_close'} 
    
    def action_button_cancel(self):
        if self.absent_lots:
            self.absent_lots.unlink()
                
        return {'type': 'ir.actions.act_window_close'} 
