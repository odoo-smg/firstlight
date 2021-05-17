# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from re import findall as regex_findall, split as regex_split

class FlspSerialNum(models.Model):
    """
        class_name: FlspSerialNum
        model_name: flsp.serialnum
        Purpose:    To create batch serial numbers
        Date:       Jan/14th/2021/R
        Author:     Sami Byaruhanga
        NOTE:       Most method logics are borrowed from stock_move (by Odoo) and FLSPstoc(by Alexandre Sausa
    """
    _name = 'flsp.serialnum'
    _description = 'FLSP Serial Num'
    _check_company_auto = True

    product_id = fields.Many2one('product.product', 'Product', domain=lambda self: self._domain_product_id(), required=True, check_company=True)
    company_id = fields.Many2one('res.company', 'Company',  stored=True, index=True,
                                 default=lambda self: self.env['res.company'].browse(
                                     self.env['res.company']._company_default_get('flsp.serialnum'))
                                )
    serial_count = fields.Integer('Number of SN', default=1, required=True)
    created_by = fields.Many2one('res.users', string="Created By", required=True, index=True, default=lambda self: self.env.user)
    create_date = fields.Datetime(string='Create Date', required=True, readonly=True, default=fields.Datetime.now)
    note = fields.Char(string='Notes')
    manufacturing_num = fields.Many2one('mrp.production', string='M/O num') #'name'
    @api.model
    def create(self, values):
        record = super(FlspSerialNum, self).create(values)
        return record

    @api.model
    def _default_nextlot(self):
        if self.env.context.get('product_id'):
            part_init = self.env.context['product_id'].default_code[0:6]
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
        print(nextlotnum)
        return nextlotnum

    first_serial = fields.Char('First SN', defualt=_default_nextlot) #Onchange fills this when the product number has been selected
    serial_num_line = fields.One2many('flsp.serialnumline', 'order_id', string='Serial Num Lines', copy=False, auto_join=True)

    def _domain_product_id(self):
        domain = ["('tracking', '!=', 'none')", "('type', '=', 'product')",
            # "'|'", "('company_id', '=', False)", "('company_id', '=', company_id)"
        ]
        if self.env.context.get('default_product_tmpl_id'):
            domain.insert(0, ("('product_tmpl_id', '=', %s)" % self.env.context['default_product_tmpl_id']))
        return '[' + ', '.join(domain) + ']'

    @api.model
    def _get_next_seqnum(self, currpartnum):
        if not currpartnum:
            retvalue = '000001'
        else:
            retvalue = ('00000' + str(int(currpartnum[-5:]) + 1))[-6:]
        # print(retvalue)
        return retvalue

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
        # print(nextlotnum)
        self.first_serial = nextlotnum
        self.name = nextlotnum
        return {
            'value': {
                'name': nextlotnum
            },
        }

    def create_serial_num(self):
        """
            Purpose: to create the serial numbers we want including the first serial number
            Method   Method logic is created based off stock move method (_generate_serial_numbers)
        """
        print("testing the assign")
        caught_initial_number = regex_findall("\d+", self.first_serial)
        initial_number = caught_initial_number[-1]
        padding = len(initial_number)
        splitted = regex_split(initial_number, self.first_serial)# We split the serial number to get the prefix and suffix.
        prefix = initial_number.join(splitted[:-1]) #initial_number could appear several times in the SN, e.g. BAV023B00001S00001
        suffix = splitted[-1]
        initial_number = int(initial_number)
        lot_names = []
        for i in range(0, self.serial_count):
            lot_names.append('%s%s%s' % (
                prefix,
                str(initial_number + i).zfill(padding),
                suffix
            ))
        print(lot_names)
        move_lines_commands = self._write_list_on_serialnumlin(lot_names)
        self.write({'serial_num_line': move_lines_commands})

        ##Writing the serial numbers in stock.production.lot
        for line in lot_names:
            self.env['stock.production.lot'].create({'name':line,
                                                     'product_id':self.product_id.id,
                                                     'company_id':self.company_id.id,
                                                     # 'product_qty':1
                                                     })
        return True

    def _write_list_on_serialnumlin(self, lot_names):
        """
            Purpose: To write the serial numbers created here on the serial num line
            Method:  Method logic is borrowed from stock move logic method - _generate_serial_move_line_commands
        """
        serial_nums = []
        for lot_name in lot_names:
            move_line_cmd = dict(serial_num=lot_name)
            serial_nums.append((0, 0, move_line_cmd))
        return serial_nums


class FlspSerialNumLine(models.Model):
    """
        Purpose: to display the serial numbers created above with the button create
    """
    _name = 'flsp.serialnumline'
    _description = "FLSP Serial Numbers for Orders"
    order_id = fields.Many2one('flsp.serialnum', string='Reference', required=True, ondelete='cascade', index=True, copy=False)
    serial_num = fields.Char("Serial Numbers") #On






