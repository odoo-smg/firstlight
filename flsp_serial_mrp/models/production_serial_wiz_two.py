# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class FlspSerialMrpWizardTwo(models.TransientModel):
    _name = 'flsp_serial_mrp.wizard.two'
    _description = "Serial Numbers on MO"

    @api.model
    def default_get(self, fields):
        res = super(FlspSerialMrpWizardTwo, self).default_get(fields)
        default_mo_id = self.env.context.get('default_mo_id') or self.env.context.get('active_id')
        if default_mo_id:
            mo = self.env['mrp.production'].browse(default_mo_id)
            if mo.exists():
                res['mo_id'] = mo.id
                if 'mo_name' in fields:
                    res['mo_name'] = mo.name
                if 'bom_id' in fields:
                    res['bom_id'] = mo.bom_id

                flsp_serial_line_ids = []
                serial_mrp = self.env['flsp.serial.mrp.two'].search([('mo_id', '=', mo.id)])
                print(serial_mrp)
                if serial_mrp:
                    for line in serial_mrp:
                        flsp_serial_line_ids.append([0, 0, {
                            'mo_id': line.mo_id.id,
                            'finished_product_id': line.product_id.id,
                            'finished_lot_id': line.finished_lot_id.id,
                            'component_product_id': line.component_id.id,
                            #'lot_id': line.component_lot_id.id,
                            'component_lot_ids': line.component_lot_ids.ids,
                            'qty': line.qty,
                            'flsp_serial_mrp_id': line.id,
                        }])
                        print(flsp_serial_line_ids)
                    res['flsp_serial_line_ids'] = flsp_serial_line_ids
                else:
                    moves = self.env['stock.move'].search([('production_id', '=', mo.id)]).ids
                    lots = self.env['stock.move.line'].search([('move_id', 'in', moves)]).lot_id
                    for lot in lots:
                        flsp_serial_line_ids.append([0, 0, {
                            'mo_id': mo.id,
                            'finished_product_id': mo.product_id.id,
                            'finished_lot_id': lot.id,
                            'component_lot_ids': lot.id,
                        }])
                    res['flsp_serial_line_ids'] = flsp_serial_line_ids

        res = self._convert_to_write(res)
        return res

    mo_id = fields.Many2one('mrp.production', string="MO", required=True)
    mo_name = fields.Char(related='mo_id.name', string="MO name", readonly=True)
    bom_id = fields.Many2one(related='mo_id.bom_id', string="Bill of Material", readonly=True)
    flsp_serial_line_ids = fields.One2many('flsp_serial_mrp.wizard.line.two', 'flsp_serial_mrp_line_id', string='Components')

    def flsp_save(self):
        self.ensure_one()
        current_ids = []
        for line in self.flsp_serial_line_ids:
            current_ids.append(line.flsp_serial_mrp_id.id)
            if line.flsp_serial_mrp_id.id:
                serial_mrp = self.env['flsp.serial.mrp.two'].search([('id', '=', line.flsp_serial_mrp_id.id)])
                if serial_mrp:
                    #serial_mrp.finished_lot_id = line.finished_lot_id.id
                    #serial_mrp.component_id = line.component_product_id.id
                    #serial_mrp.component_lot_id = line.lot_id.id
                    serial_mrp.component_lot_ids = line.component_lot_ids.ids
                    #serial_mrp.qty = line.qty
            else:
                new = self.env['flsp.serial.mrp.two'].create({
                    'mo_id': line.mo_id.id,
                    'product_id': line.finished_product_id.id,
                    'finished_lot_id': line.finished_lot_id.id,
                    'component_id': line.finished_product_id.id,
                    'component_lot_ids': line.component_lot_ids,
                    'qty': line.qty,
                })
                current_ids.append(new.id)
        serial_mrp = self.env['flsp.serial.mrp.two'].search([('mo_id', '=', self.mo_id.id), ('id', 'not in', current_ids)])
        if serial_mrp:
            for line in serial_mrp:
                print('deleting')
                line.unlink()


class FlspMrpSerialLineTwo(models.TransientModel):
    """Sales Approval"""
    _name = "flsp_serial_mrp.wizard.line.two"
    _description = 'Serials on MOs'

    def _get_mo(self):
        res = self.env.context.get('default_mo_id') or self.env.context.get('active_id')
        return res

    mo_id = fields.Many2one('mrp.production', string="MO", default=_get_mo)

    finished_product_id = fields.Many2one('product.product', string='Finished Product')
    finished_lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number')
    component_product_id = fields.Many2one('product.product', string='Component')

    component_lot_ids = fields.Many2many('stock.production.lot', string='Components Lots')

    qty = fields.Float('Qty', default=1, digits='Product Unit of Measure', required=True)
    flsp_serial_mrp_line_id = fields.Many2one('flsp_serial_mrp.wizard.two')
    sequence = fields.Integer(string='Sequence', default=10)
    product_template_id = fields.Many2one('product.template', string='Product Template')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', default=1.0)
    flsp_serial_mrp_id = fields.Many2one('flsp.serial.mrp.two', string='Flsp Serial MRP')

