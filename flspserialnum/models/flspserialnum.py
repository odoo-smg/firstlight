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

        # existing serial numbers in the range in stock.production.lot
        existing_lots = self.env['stock.production.lot'].search([('name', 'in', lot_names), ('product_id', '=', self.product_id.id), ('company_id', '=', self.company_id.id)])
        
        # all created serial numbers in stock.production.lot associated with the order_id
        created_lot_names = self.env['flsp.serialnumline'].search([('order_id', '=', self.id)]).mapped('serial_num')

        if len(existing_lots) > 0 or (len(created_lot_names) > len(lot_names)):
            self._write_existing_serialnum_lines(existing_lots)

            absent_lot_names = []
            for line in lot_names:
                if not line in existing_lots.mapped('name'):
                    absent_lot_names.append(line)
            
            extra_lot_names = []
            for line in created_lot_names:
                if not line in lot_names:
                    extra_lot_names.append(line)

            # open wizard to let user choose what to do next
            return {
                'name': 'FLSP Serial Number Wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('flspserialnum.flsp_serial_num_wizard_form_view').id,
                'res_model': 'flsp.serial.num.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_order_id': self.id,
                    'default_existing_lot_names': existing_lots.mapped('name'),
                    'default_absent_lot_names': absent_lot_names,
                    'default_extra_lot_names': extra_lot_names,
                }
            }
        else:
            lots = self.create_absent_serial_num(lot_names)
            self._write_existing_serialnum_lines(lots)

        return True

    def create_absent_serial_num(self, absent_lot_names):
        for line in absent_lot_names:
            self.env['stock.production.lot'].create({'name':line,
                                                     'product_id':self.product_id.id,
                                                     'company_id':self.company_id.id,
                                                     # 'product_qty':1
                                                     })
        return self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id), ('company_id', '=', self.company_id.id), ('name', 'in', absent_lot_names)])

    def _write_absent_serialnum_lines(self, lot_names):
        for lot_name in lot_names:
            lot = self.env['flsp.serialnumline'].search([('order_id', '=', self.id), ('serial_num', '=', lot_name)])
            if lot:
                continue
            else:
                self.env['flsp.serialnumline'].create({
                    'order_id': self.id,
                    'serial_num': lot_name,
                })

        return self.env['flsp.serialnumline'].search([('order_id', '=', self.id), ('serial_num', 'in', lot_names)])

    def _write_existing_serialnum_lines(self, lots):
        for lot in lots:
            lot_in_line = self.env['flsp.serialnumline'].search([('order_id', '=', self.id), ('serial_num', '=', lot.name)])
            if lot_in_line:
                continue
            else:
                self.env['flsp.serialnumline'].create({
                    'order_id': self.id,
                    'serial_num': lot.name,
                })
                                      
    def unlink_serial_num(self, lot_names):
        self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id), ('company_id', '=', self.company_id.id), ('name', 'in', lot_names)]).unlink()

class FlspSerialNumLine(models.Model):
    """
        Purpose: to display the serial numbers created above with the button create
    """
    _name = 'flsp.serialnumline'
    _description = "FLSP Serial Numbers for Orders"
    order_id = fields.Many2one('flsp.serialnum', string='Reference', required=True, ondelete='cascade', index=True, copy=False)
    serial_num = fields.Char("Serial Numbers") #On
