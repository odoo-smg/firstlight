# -*- coding: utf-8 -*-

from odoo import fields, models, api


class flspstocklot(models.Model):
    _inherit = 'stock.production.lot'
    _check_company_auto = True

    flsp_linux_ethernet = fields.Char("Linux Ethernet")
    flsp_linux_powerline = fields.Char("Linux Powerline")
    flsp_qcanum = fields.Char("QCA7000")

    @api.model
    def _default_nextlot(self):

        if self.env.context.get('product_id'):
            part_init = self.env.context['product_id'].default_code[0:6]
        else:
            part_init = 'abc'
        print("select max(name) as code from stock_production_lot where name like '" + part_init + "%' ")
        self._cr.execute("select max(name) as code from stock_production_lot where name like '" + part_init + "%' and length(name) = 13")
        retvalue = self._cr.fetchall()
        returned_registre = retvalue[0]
        nextseqnum = self._get_next_seqnum(returned_registre[0])
        if part_init == 'abc':
            part_init = ''
        nextlotnum = part_init
        print(nextlotnum)
        nextlotnum = nextlotnum + "_"
        print(nextlotnum)
        nextlotnum = nextlotnum + nextseqnum
        print(nextlotnum)
        return nextlotnum

    name = fields.Char('Lot/Serial Number', default=_default_nextlot,required=True, help="Unique Lot/Serial Number")

    @api.model
    def _get_next_seqnum(self, currpartnum):
        print(currpartnum)
        if not currpartnum:
            retvalue = '000001'
        else:
            retvalue = ('00000' + str(int(currpartnum[-5:]) + 1))[-6:]

        print(retvalue)
        return retvalue

    @api.onchange('product_id')
    def flsp_product_id_lot_onchange(self):
        if self.product_id:
            part_init = self.product_id.default_code[0:6]
        else:
            part_init = 'abc'
        print("select max(name) as code from stock_production_lot where name like '" + part_init + "%' ")
        self._cr.execute("select max(name) as code from stock_production_lot where name like '" + part_init + "%' and length(name) = 13")
        retvalue = self._cr.fetchall()
        returned_registre = retvalue[0]
        nextseqnum = self._get_next_seqnum(returned_registre[0])
        if part_init == 'abc':
            part_init = ''
        nextlotnum = part_init
        print(nextlotnum)
        nextlotnum = nextlotnum + "_"
        print(nextlotnum)
        nextlotnum = nextlotnum + nextseqnum
        print(nextlotnum)
        self.name = nextlotnum
        return {
            'value': {
                'name': nextlotnum
            },
        }
