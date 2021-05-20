# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class FlspSerialMrpWizard(models.TransientModel):
    _name = 'flsp_serial_mrp.wizard'
    _description = "Serial Numbers on MO"

    @api.model
    def default_get(self, fields):
        res = super(FlspSerialMrpWizard, self).default_get(fields)
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
                serial_mrp = self.env['flsp.serial.mrp'].search([('mo_id', '=', mo.id)])
                if serial_mrp:
                    for line in serial_mrp:
                        flsp_serial_line_ids.append([0, 0, {
                            'mo_id': line.mo_id.id,
                            'finished_product_id': line.product_id.id,
                            'finished_lot_id': line.finished_lot_id.id,
                            'component_product_id': line.component_id.id,
                            'lot_id': line.component_lot_id.id,
                            'qty': line.qty,
                            'flsp_serial_mrp_id': line.id,
                        }])
                    res['flsp_serial_line_ids'] = flsp_serial_line_ids

        res = self._convert_to_write(res)
        return res

    mo_id = fields.Many2one('mrp.production', string="MO", required=True)
    mo_name = fields.Char(related='mo_id.name', string="MO name", readonly=True)
    bom_id = fields.Many2one(related='mo_id.bom_id', string="Bill of Material", readonly=True)
    flsp_serial_line_ids = fields.One2many('flsp_serial_mrp.wizard.line', 'flsp_serial_mrp_line_id', string='Components')

    def flsp_save(self):
        self.ensure_one()
        current_ids = []
        if self.flsp_serial_line_ids:
            for line in self.flsp_serial_line_ids:
                current_ids.append(line.flsp_serial_mrp_id.id)
                if line.flsp_serial_mrp_id.id:
                    serial_mrp = self.env['flsp.serial.mrp'].search([('id', '=', line.flsp_serial_mrp_id.id)])
                    if serial_mrp:
                        serial_mrp.finished_lot_id = line.finished_lot_id.id
                        serial_mrp.component_id = line.component_product_id.id
                        serial_mrp.component_lot_id = line.lot_id.id
                        serial_mrp.qty = line.qty
                else:
                    new = self.env['flsp.serial.mrp'].create({
                        'mo_id': line.mo_id.id,
                        'product_id': line.finished_product_id.id,
                        'finished_lot_id': line.finished_lot_id.id,
                        'component_id': line.component_product_id.id,
                        'component_lot_id': line.lot_id.id,
                        'qty': line.qty,
                    })
                    current_ids.append(new.id)
        serial_mrp = self.env['flsp.serial.mrp'].search([('mo_id', '=', self.mo_id.id), ('id', 'not in', current_ids)])
        if serial_mrp:
            for line in serial_mrp:
                line.unlink()


class FlspMrpSerialLine(models.TransientModel):
    """Sales Approval"""
    _name = "flsp_serial_mrp.wizard.line"
    _description = 'Serials on MOs'

    def _get_mo(self):
        res = self.env.context.get('default_mo_id') or self.env.context.get('active_id')
        return res

    def _get_fp(self):
        mo_id = self.env.context.get('default_mo_id') or self.env.context.get('active_id')
        mo = self.env['mrp.production'].browse(mo_id)
        res = mo.product_id
        return res

    def _get_lots(self):
        mo_id = self.env.context.get('default_mo_id') or self.env.context.get('active_id')
        moves = self.env['stock.move'].search([('production_id', '=', mo_id)]).ids
        res = self.env['stock.move.line'].search([('move_id', 'in', moves)]).lot_id
        return res

    def _get_moves(self):
        mo_id = self.env.context.get('default_mo_id') or self.env.context.get('active_id')
        moves = self.env['stock.move'].search([('production_id', '=', mo_id)]).ids
        res = self.env['stock.move.line'].search([('move_id', 'in', moves)])
        return res

    mo_id = fields.Many2one('mrp.production', string="MO", default=_get_mo)
    finished_move_line_ids = fields.Many2many('stock.move.line', string='Move Lines', default=_get_moves)
    finished_lot_ids = fields.Many2many('stock.production.lot', string='Lots', default=_get_lots)

    finished_product_id = fields.Many2one('product.product', string='Finished Product', default=_get_fp)
    finished_lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', domain="[('id', 'in', finished_lot_ids)]")
    component_product_id = fields.Many2one('product.product', string='Component', required=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', required=True, domain="[('product_id', '=', component_product_id)]")
    qty = fields.Float('Qty', default=1, digits='Product Unit of Measure', required=True)
    flsp_serial_mrp_line_id = fields.Many2one('flsp_serial_mrp.wizard')
    sequence = fields.Integer(string='Sequence', default=10)
    product_template_id = fields.Many2one('product.template', string='Product Template')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', default=1.0)
    flsp_serial_mrp_id = fields.Many2one('flsp.serial.mrp', string='Flsp Serial MRP')

