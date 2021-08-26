# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from re import findall as regex_findall, split as regex_split

import logging
_logger = logging.getLogger(__name__)


class flspmrpwipproduction(models.Model):
    _inherit = 'flsp.serialnum'
    _check_company_auto = True

    name = fields.Char(string='name')

    def name_get(self):
        return [(
            record.id,
            record.name or str(record.id)
        ) for record in self]

    @api.model
    def create(self, vals):
        prefix = self.env['ir.sequence'].next_by_code('flspserialnum') or ''
        vals['name'] = prefix

        return super(flspmrpwipproduction, self).create(vals)

    @api.onchange('product_id')
    def flsp_product_id_lot_onchange(self):
        if self.product_id:
            part_init = self.product_id.default_code[0:6]
        else:
            part_init = 'abc'
        self._cr.execute("select max(name) as code from stock_production_lot where name like '" + part_init + "%' and length(name) = 13")
        retvalue = self._cr.fetchall()
        returned_registre = retvalue[0]
        nextseqnum = self._get_next_seqnum(returned_registre[0])
        if part_init == 'abc':
            part_init = ''
        nextlotnum = part_init
        nextlotnum = nextlotnum + "_"
        nextlotnum = nextlotnum + nextseqnum
        self.first_serial = nextlotnum
        return {
            'value': {
                'first_serial': nextlotnum
            },
        }

    def _write_existing_serialnum_lines(self, lots):
        # overwrite the method defined in firstlight\flspserialnum\models\flspserialnum.py
        for lot in lots:
            lot_in_line = self.env['flsp.serialnumline'].search([('order_id', '=', self.id), ('serial_num', '=', lot.name)])
            if lot_in_line:
                continue
            else:
                self.env['flsp.serialnumline'].create({
                    'order_id': self.id,
                    'serial_num': lot.name,
                    'lot_id': lot.id,
                })

    def _update_absent_serialnum_lines_with_lot_id(self, lots):
        for lot in lots:
            lot_in_line = self.env['flsp.serialnumline'].search([('order_id', '=', self.id), ('serial_num', '=', lot.name)])
            if lot_in_line:
                lot_in_line.write({ 'lot_id': lot.id })

class flspMrpBatchSerialLine(models.Model):
    _inherit = 'flsp.serialnumline'
    _check_company_auto = True

    lot_id = fields.Many2one('stock.production.lot', string='Lot/Serial Number')
    
class flspMrpBatchSerialWizard(models.TransientModel):
    _inherit = 'flsp.serial.num.wizard'

    def action_button_continue_creation(self):
        if len(self.absent_lots) > 0:
            created_absent_lots = self.order_id.create_absent_serial_num(self.absent_lots.mapped('serial_num'))
            self.order_id._update_absent_serialnum_lines_with_lot_id(created_absent_lots)
            
        if len(self.extra_lots) > 0:
            self.order_id.unlink_serial_num(self.extra_lots.mapped('serial_num'))
            self.extra_lots.unlink()

        return {'type': 'ir.actions.act_window_close'} 

