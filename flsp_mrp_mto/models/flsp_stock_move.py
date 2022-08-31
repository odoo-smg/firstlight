# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import timedelta
import dateutil.rrule as rrule
from datetime import datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class FlspMtoStockMove(models.Model):
    _inherit = 'stock.move'

    sale_id = fields.Many2one('sale.order', string="Customer", compute='_cal_sale_order', store=True)
    mo_id = fields.Many2one('mrp.production', string="MO")
    is_today = fields.Boolean('Today', compute='_compute_shipping_date')
    is_week = fields.Boolean('Week', compute='_compute_shipping_date')

    @api.depends('date')
    def _compute_shipping_date(self):
        current_date = datetime.now()
        current_date_str = str(current_date)[0:10]
        date_week = current_date + timedelta(days=6-current_date.weekday())
        date_week_str = str(date_week)[0:10]
        for move in self:
            move.is_today = False
            move.is_week = False
            if str(move.date)[0:10] == current_date_str:
                move.is_today = True
            elif str(move.date)[0:10] <= date_week_str:
                move.is_week = True


    @api.depends('picking_id')
    def _cal_sale_order(self):
        for move in self:
            sales = self.env['sale.order'].search([('name', '=', move.origin)])
            if sales:
                move.sale_id = sales.id

    def execute_suggestion(self):
        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA/WIP')], limit=1)
        stock_location = self.env['stock.location'].search([('complete_name', '=', 'WH/Stock')], limit=1)
        mrp_picking_type = self.env['stock.picking.type'].search([('name', '=', 'Manufacturing'), ('active', '=', True), ('company_id', '=', self.env.company.id)])
        for item in self:
            if item.mo_id:
                continue
            bom_id = self.env['mrp.bom']._bom_find(product=item.product_id)
            if not bom_id:
                raise ValidationError(("BOM not found for product: "+item.product_id.default_code))
                #item.rationale += "<br/> |"
                #item.rationale += "<br/> |"
                #item.rationale += "<br/>A T T E N T I O N: "
                #item.rationale += "<br/> **** The attempt to create MO has failed *** "
                #item.rationale += "<br/> Product has no Bill of Materials."
                #item.rationale += "<br/> User: " + self.env['res.users'].search([('id', '=', self._uid)]).name
                continue

            mo = self.env['mrp.production'].create({
                'product_id': item.product_id.id,
                'bom_id': bom_id.id,
                'product_uom_id': item.product_id.uom_id.id,
                'product_qty': item.product_uom_qty,
                'date_planned_start': datetime.combine(item.date, datetime.now().time()),
                'date_planned_finished': datetime.combine(item.date, datetime.now().time()),
                'date_deadline': datetime.combine(item.date, datetime.now().time()),
                'location_src_id': mrp_picking_type.default_location_src_id.id if mrp_picking_type else pa_location.id,
                'location_dest_id': stock_location.id,
                'origin': item.origin,
            })

            list_move_raw = [(4, move.id) for move in mo.move_raw_ids.filtered(lambda m: not m.bom_line_id)]
            moves_raw_values = mo._get_moves_raw_values()
            move_raw_dict = {move.bom_line_id.id: move for move in mo.move_raw_ids.filtered(lambda m: m.bom_line_id)}
            for move_raw_values in moves_raw_values:
                if move_raw_values['bom_line_id'] in move_raw_dict:
                    # update existing entries
                    list_move_raw += [(1, move_raw_dict[move_raw_values['bom_line_id']].id, move_raw_values)]
                else:
                    # add new entries
                    list_move_raw += [(0, 0, move_raw_values)]
            mo.move_raw_ids = list_move_raw
            item.mo_id = mo.id

        return
