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

    def _write_list_on_serialnumlin(self, lot_names):
        """
            Purpose: To write the serial numbers created here on the serial num line
            Method:  Method logic is borrowed from stock move logic method - _generate_serial_move_line_commands
        """
        serial_nums = []
        for lot_name in lot_names:
            move_line_cmd = dict(serial_num=lot_name[1], lot_id=lot_name[0])
            serial_nums.append((0, 0, move_line_cmd))
        return serial_nums

    def create_serial_num(self):
        """
            Purpose: to create the serial numbers we want including the first serial number
            Method   Method logic is created based off stock move method (_generate_serial_numbers)
        """
        caught_initial_number = regex_findall("\d+", self.first_serial)
        initial_number = caught_initial_number[-1]
        padding = len(initial_number)
        splitted = regex_split(initial_number, self.first_serial)# We split the serial number to get the prefix and suffix.
        prefix = initial_number.join(splitted[:-1]) #initial_number could appear several times in the SN, e.g. BAV023B00001S00001
        suffix = splitted[-1]
        initial_number = int(initial_number)
        lot_names = []
        for i in range(0, self.serial_count):
            lot_names.append([False, '%s%s%s' % (
                prefix,
                str(initial_number + i).zfill(padding),
                suffix
            )])

        for line in lot_names:
            lot = self.env['stock.production.lot'].create({'name':line[1],
                                                     'product_id':self.product_id.id,
                                                     'company_id':self.company_id.id,
                                                     # 'product_qty':1
                                                     })
            if lot:
                line[0] = lot.id

        move_lines_commands = self._write_list_on_serialnumlin(lot_names)
        self.write({'serial_num_line': move_lines_commands})

        ##Writing the serial numbers in stock.production.lot
        return True

class flspMrpBatchSerialLine(models.Model):
    _inherit = 'flsp.serialnumline'
    _check_company_auto = True

    lot_id = fields.Many2one('stock.production.lot', string='Lot/Serial Number')

