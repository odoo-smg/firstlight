# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class flspmrpbatchproduction(models.TransientModel):
    _inherit = 'mrp.product.produce'
    _check_company_auto = True

    flsp_batch_serial_id = fields.Many2one('flsp.serialnum', string="Serial Batch", compute="_flsp_compute_serial")
    flsp_serial_num_line = fields.Many2many('stock.production.lot', string='FLSP batch Lots',
                                            compute="_flsp_compute_serial")


    @api.onchange('flsp_serial_num_line')
    def _onchange_flsp_serial_num_line(self):
        res = {}
        if self.flsp_batch_serial_id:
            res = {'options': {'no_create': True},
                   'domain': {'finished_lot_id': [('id','in', self.flsp_serial_num_line.ids)]},
                   }
        return res

    @api.depends('production_id')
    def _flsp_compute_serial(self):
        if self.production_id.flsp_batch_serial_id:
            self.flsp_batch_serial_id = self.production_id.flsp_batch_serial_id.id
            my_lots = []
            first_lot = False
            for line in self.production_id.flsp_batch_serial_id.serial_num_line:
                jump_next = False
                for finished in self.production_id.finished_move_line_ids:
                    if line.lot_id.id == finished.lot_id.id:
                        jump_next = True
                if not jump_next:
                    my_lots.append(line.lot_id.id)
                    if not first_lot:
                        first_lot = line.lot_id.id

            self.flsp_serial_num_line = my_lots
            self.finished_lot_id = first_lot
        else:
            self.flsp_batch_serial_id = False
            self.flsp_serial_num_line = False

    def _update_workorder_lines(self):

        """
        Overrides the function to call it again
        used to sort the items by tracking.
        """
        res = super(flspmrpbatchproduction, self)._update_workorder_lines()
        tmp = []
        for line in res['to_create']:
            #print('move_id: '+str(line['move_id'])+' prod_id:'+str(line['product_id'])+' qty: '+str(line['qty_to_consume']))
            product_id = self.env['product.product'].search([('id', '=', line['product_id'])])
            if product_id.tracking == 'serial':
                line['product_tracking'] = '1'
            elif product_id.tracking == 'lot':
                line['product_tracking'] = '2'
            else:
                line['product_tracking'] = '3'
            tmp.append(line)
        tmp.sort(key=lambda x: x['product_tracking'])

        res['to_create'] = tmp
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        """
        Overrides orm field_view_get.
        @return: Dictionary of Fields, arch and toolbar.
        """
        res = {}
        #res = super(employee_exit, self).fields_view_get(cr, user, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        res = super(flspmrpbatchproduction, self).fields_view_get(view_id, view_type, toolbar, submenu)
        default_mo_id = self.env.context.get('prouction_id')
        active_id = self.env.context.get('active_id')

        from lxml import etree
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='finished_lot_id']"):
            if self.flsp_serial_num_line:
                node.set('domain', "[('id','in', flsp_serial_num_line)]")
        res['arch'] = etree.tostring(doc)
        return res
