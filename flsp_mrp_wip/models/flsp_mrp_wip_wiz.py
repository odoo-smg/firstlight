# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, datetime
import logging
_logger = logging.getLogger(__name__)

class FlspMrpWipWiz(models.TransientModel):
    _name = 'flsp.mrp.wip.wiz'
    _description = "Components to be transferred from Stock to WIP"

    mo_id = fields.Many2one('mrp.production', string="MO", required=True)
    mo_name = fields.Char(related='mo_id.name', string="MO name", readonly=True)
    bom_id = fields.Many2one(related='mo_id.bom_id', string="Bill of Material", readonly=True)
    flsp_wip_transfer_ids = fields.One2many(related='mo_id.flsp_wip_transfer_ids', string="Transfer Created: ")
    bom_products = fields.One2many(comodel_name='flsp.mrp.wip.wiz.product', inverse_name='production_id',
                                   string="products in BoM structure", readonly=False)
    bom_missed = fields.One2many(comodel_name='flsp.mrp.wip.wiz.comp', inverse_name='production_id',
                                   string="products in BoM structure", readonly=False)
    new_mo_ids = fields.One2many(comodel_name='mrp.production', inverse_name='id', string="New MOs")
    bom_level = fields.Integer(string="BOM Level")

    show_missing = fields.Boolean(string="Show Missing Only", default=True)
    show_sublevels = fields.Boolean(string="Show Sub-levels", default=False)
    wip_id = fields.Many2one('stock.picking', string="Transfer Created Old: ")

    @api.model
    def default_get(self, fields):
        res = super(FlspMrpWipWiz, self).default_get(fields)
        default_mo_id = self.env.context.get('default_mo_id')
        show_sublevels = self.env.context.get('show_sublevels')
        stock_picking = self.env.context.get('wip_id')

        if default_mo_id:
            mo = self.env['mrp.production'].browse(default_mo_id)
            if mo.exists():
                if not stock_picking:
                    picking = self.env['stock.picking'].search(['&', ('flsp_mo_wip_id', '=',mo.id), ('state', '!=', 'cancel')], limit=1)
                    if picking:
                        stock_picking = picking
                res['mo_id'] = mo.id
                if 'mo_name' in fields:
                    res['mo_name'] = mo.name
                if 'bom_id' in fields:
                    res['bom_id'] = mo.bom_id
                if 'show_sublevels' in fields:
                    res['show_sublevels'] = show_sublevels
                if 'wip_id' in fields and stock_picking:
                    res['wip_id'] = stock_picking
                if 'bom_products' in fields:
                    res['bom_products'] = self._calc_bom_products(mo, show_sublevels, False)
                    res['bom_missed'] = self._calc_bom_products(mo, show_sublevels, True)

        default_new_mo_items = self.env.context.get('default_new_mo_items')
        if default_new_mo_items:
            res['new_mo_ids'] = self.env['mrp.production'].browse(default_new_mo_items)

        res = self._convert_to_write(res)
        return res

    def _calc_bom_products(self, mo, show_sublevels, missing):

        bom_id = mo.bom_id
        mo_qty = mo.product_qty
        starting_factor = bom_id.product_uom_id._compute_quantity(
            bom_id.product_qty, bom_id.product_tmpl_id.uom_id, round=False
        )
        if not show_sublevels:
            totals = {}
            # shows only the first level - those are products in the stock_move.
            move_raw = self.env['stock.move'].search([('raw_material_production_id', '=', mo.id)])
            if move_raw:
                for raw_line in move_raw:
                    totals[len(totals)+1] = {'total': raw_line.product_qty/mo_qty, 'level': 1, 'bom': False, 'type': False, 'bom_plm': True, 'track': raw_line.product_id.tracking, 'prod': raw_line.product_id}
        else:
            totals = bom_id._get_flattened_totals(factor=starting_factor)

        # retrieve the product ids from the list
        prod_list = []
        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id

        for order, total_qty in totals.items():
            proceed = True
            if route_buy not in total_qty['prod'].route_ids.ids or total_qty['level'] > 1: #total_qty['bom'] and ('flsp_backflush' in self.env['product.template']._fields) and total_qty['prod'].flsp_backflush == False:
                proceed = False

            if show_sublevels:
                proceed = True

            if proceed:
                # add product in the list
                prod = total_qty['prod']
                required_qty = mo_qty * total_qty['total']
                reserved_qty = self.get_reserved(prod.id, mo)
                remaining_qty = required_qty - reserved_qty
                flsp_wip_qty = self.get_wip_qty(prod.id)
                prod.get_wip_qty()
                prod.get_stock_qty()

                is_missing = True
                keep_creating = True
                if remaining_qty == 0:
                    is_missing = False
                    keep_creating = False
                else:
                    if flsp_wip_qty > remaining_qty:
                        keep_creating = False


                # search prod in prod_list and add up mo_required_qty if found
                prod_in_list = self.search_product_from_list(prod.id, prod_list)

                if not missing:
                    keep_creating = True

                if keep_creating:
                    if prod_in_list:
                        prod_in_list['mo_required_qty'] += required_qty
                        prod_in_list['remaining_qty'] = prod_in_list['mo_required_qty']-prod_in_list['reserved_qty']
                        prod_in_list['adjusted_qty'] = prod_in_list['remaining_qty']
                    else:
                        prod_list.append([0, 0, {
                            'production_id': self.id,
                            'product_id': prod.id,
                            'part_number': prod.default_code,
                            'product_name': prod.name,
                            'stock_qty': prod.flsp_stock_qty,
                            'wip_qty': flsp_wip_qty,
                            'mo_required_qty': required_qty,
                            'is_missing': is_missing,
                            'reserved_qty': reserved_qty,
                            'remaining_qty': remaining_qty,
                            'adjusted_qty': remaining_qty,
                            'flsp_sd_location': prod.flsp_sd_location.id,
                            'bom_level': total_qty['level'],
                        }])
        return prod_list


    def get_reserved(self, prod_id, mo):
        """
            Purpose: get the WIP qty for the product
        """
        reserved = 0
        move_raw = self.env['stock.move'].search(['&', ('raw_material_production_id', '=', mo.id),('product_id', '=', prod_id)])
        move_line = False
        if move_raw:
            move_line = self.env['stock.move.line'].search([('move_id', 'in', move_raw.ids)])

        if move_line:
            for line in move_line:
                reserved += line.product_uom_qty

        return reserved

    def get_wip_qty(self, prod_id):
        """
            Purpose: get the WIP qty for the product
        """
        pa_wip_qty = 0

        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')]).parent_path
        if not pa_location:
            raise UserError('WIP Stock Location is missing')
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location+'%')]).ids
        if not pa_wip_locations:
            raise UserError('WIP Stock Location is missing')

        stock_quant = self.env['stock.quant'].search(
            ['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', prod_id)])
        for stock_lin in stock_quant:
            pa_wip_qty += stock_lin.quantity-stock_lin.reserved_quantity

        return pa_wip_qty

    def search_product_from_list(self, id, prod_list):
        for prod_entry in prod_list:
            if id == prod_entry[2]['product_id']:
                return prod_entry[2]

        return False

    def button_create_wip(self):
        date_now = datetime.now()
        date_start = date_now.today() + timedelta(days=1)
        date_end = date_now.today() + timedelta(days=15)
        stock_picking = False
        picking_type_id = self.get_picking_type()

        targetProd = self.env['flsp.mrp.wip.wiz.product'].search(
            ['&', ('production_id', '=', self.id), ('selected', '=', True)])
        if len(targetProd) == 0:
            targetProd = self.env['flsp.mrp.wip.wiz.comp'].search(
                ['&', ('production_id', '=', self.id), ('selected', '=', True)])

        count_products = 0
        count_by_resp = {}
        count_by_resp['resp'] = [0]
        count_by_resp['total'] = {0: 0}
        count_by_resp['prod'] = {0: 0}
        count_by_resp['prod'][0] = []
        wip_resp = self.env['flsp.wip.responsible'].search([])
        for each in wip_resp:
            if each.responsible.id not in count_by_resp['resp']:
                count_by_resp['resp'].append(each.responsible.id)
                count_by_resp['total'][each.responsible.id] = 0
                count_by_resp['prod'][each.responsible.id] = []

        for prod in targetProd:
            for responsible in wip_resp:
                loc_name = ''
                included = False
                if prod.flsp_sd_location:
                    parent_locations = []
                    if responsible.parent_location.complete_name:
                        parent_locations = self.env['stock.location'].search([('complete_name', 'like', responsible.parent_location.complete_name + '%')]).ids
                    if responsible.text_location and responsible.text_location in prod.flsp_sd_location.complete_name:
                        count_by_resp['total'][responsible.responsible.id] += 1
                        count_by_resp['prod'][responsible.responsible.id].append(prod.product_id.id)
                        included = True
                        break
                    elif prod.flsp_sd_location.id in parent_locations:
                        count_by_resp['total'][responsible.responsible.id] += 1
                        count_by_resp['prod'][responsible.responsible.id].append(prod.product_id.id)
                        included = True
                        break
            if not included:
                count_by_resp['total'][0] += 1
                count_by_resp['prod'][0].append(prod.product_id.id)
            count_products += 1

        if count_products > 0:
            for resp in count_by_resp['resp']:
                if count_by_resp['total'][resp]>0:
                    user = self.env['res.users'].sudo().browse(resp)
                    partner_id = False
                    if user:
                        partner_id = user.partner_id.id
                    if resp == 0:
                        partner_id = False
                    create_val = {
                        'origin': self.mo_id.name+'WIP-TRANSFER',
                        'picking_type_id': picking_type_id.id,
                        'location_id': picking_type_id.default_location_src_id.id,
                        'partner_id': partner_id,
                        'location_dest_id': picking_type_id.default_location_dest_id.id,
                        'flsp_mo_wip_id': self.mo_id.id,
                    }
                    stock_picking = self.env['stock.picking'].create(create_val)

                if stock_picking:
                    for prod in targetProd:
                        if prod.product_id.id in count_by_resp['prod'][resp]:
                            stock_move = self.env['stock.move'].create({
                                'name': prod.product_id.name,
                                'product_id': prod.product_id.id,
                                'product_uom': prod.product_id.uom_id.id,
                                'product_uom_qty': prod.adjusted_qty,
                                'picking_id': stock_picking.id,
                                'location_id': picking_type_id.default_location_src_id.id,
                                'location_dest_id': picking_type_id.default_location_dest_id.id,
                            })
        wip_id = False
        if stock_picking:
            wip_id = stock_picking.id
        view_id = self.env.ref('flsp_mrp_wip.flsp_mrp_wip_wiz_form_view').id

        return {
            'name': 'WIP Transfer',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flsp.mrp.wip.wiz',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_mo_id': self.mo_id.id,
                'show_sublevels': self.show_sublevels,
                'wip_id': wip_id,
            }
        }

    def button_show_all(self):
        view_id = self.env.ref('flsp_mrp_wip.flsp_mrp_wip_wiz_form_view').id
        return {
            'name': 'WIP Transfer',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flsp.mrp.wip.wiz',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_mo_id': self.mo_id.id,
                'show_sublevels': True,
                'wip_id': False,
            }
        }

    def button_show_lv1(self):
        view_id = self.env.ref('flsp_mrp_wip.flsp_mrp_wip_wiz_form_view').id
        return {
            'name': 'WIP Transfer',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flsp.mrp.wip.wiz',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_mo_id': self.mo_id.id,
                'show_sublevels': False,
                'wip_id': False,
            }
        }


    def get_bom(self, prod, mo_id):
        # copy from onchange_product_id() in model 'mrp.production'
        return self.env['mrp.bom']._bom_find(product=prod.product_id, picking_type=mo_id.picking_type_id,
                                             company_id=mo_id.company_id.id, bom_type='normal')

    def get_picking_type(self):
        # copy from _onchange_bom_id() in model 'mrp.production'
        picking_id = self.env['stock.picking.type'].search([('sequence_code', '=', 'INT')], limit=1)
        return picking_id

    def set_bom_product(self, new_mo):
        # call _onchange_move_raw() in model 'mrp.production'
        new_mo._onchange_move_raw()

    def set_locations(self, new_mo):
        # call onchange_picking_type() in model 'mrp.production'
        new_mo.onchange_picking_type()


class FlspMrpWipWizProduct(models.TransientModel):
    _name = 'flsp.mrp.wip.wiz.product'
    _description = "Product in the BoM structure for wip transfer"

    selected = fields.Boolean('Selected')
    production_id = fields.Many2one('flsp.mrp.wip.wiz')
    product_id = fields.Many2one('product.product', store=True, string='Product')
    part_number = fields.Char(related='product_id.default_code')
    product_name = fields.Char(related='product_id.name')
    stock_qty = fields.Float('Stock Qty', default=0.0, digits='Product Unit of Measure', readonly=True)
    wip_qty = fields.Float('WIP Qty', default=0.0, digits='Product Unit of Measure', readonly=True)
    reserved_qty = fields.Float('Reserved', default=0.0, digits='Product Unit of Measure', readonly=True)
    remaining_qty = fields.Float('Required', default=0.0, digits='Product Unit of Measure', readonly=True)
    mo_required_qty = fields.Float('MO Required Qty', default=0.0, digits='Product Unit of Measure', readonly=True)
    adjusted_qty = fields.Float('Adjusted', default=0.0, digits='Product Unit of Measure', required=True)
    bom_level = fields.Integer(string="BOM Level")
    flsp_sd_location = fields.Many2one('stock.location', string='Standard Location', related='product_id.flsp_sd_location')
    is_missing = fields.Boolean(string="Is Missing", default=True)

class FlspMrpWipWizProduct(models.TransientModel):
    _name = 'flsp.mrp.wip.wiz.comp'
    _description = "Missed Component in the BoM structure for wip transfer"

    selected = fields.Boolean('Selected')
    production_id = fields.Many2one('flsp.mrp.wip.wiz')
    product_id = fields.Many2one('product.product', store=True, string='Product')
    part_number = fields.Char(related='product_id.default_code')
    product_name = fields.Char(related='product_id.name')
    stock_qty = fields.Float('Stock Qty', default=0.0, digits='Product Unit of Measure', readonly=True)
    wip_qty = fields.Float('WIP Qty', default=0.0, digits='Product Unit of Measure', readonly=True)
    reserved_qty = fields.Float('Reserved', default=0.0, digits='Product Unit of Measure', readonly=True)
    remaining_qty = fields.Float('Required', default=0.0, digits='Product Unit of Measure', readonly=True)
    mo_required_qty = fields.Float('MO Required Qty', default=0.0, digits='Product Unit of Measure', readonly=True)
    adjusted_qty = fields.Float('Adjusted', default=0.0, digits='Product Unit of Measure', required=True)
    bom_level = fields.Integer(string="BOM Level")
    flsp_sd_location = fields.Many2one('stock.location', string='Standard Location', related='product_id.flsp_sd_location')
    is_missing = fields.Boolean(string="Is Missing", default=True)
