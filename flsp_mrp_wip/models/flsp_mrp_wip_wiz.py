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
    bom_products = fields.One2many(comodel_name='flsp.mrp.wip.wiz.product', inverse_name='production_id',
                                   string="products in BoM structure")
    new_mo_ids = fields.One2many(comodel_name='mrp.production', inverse_name='id', string="New MOs")
    bom_level = fields.Integer(string="BOM Level")

    show_sublevels = fields.Boolean(string="Show Sub-levels", default=False)
    wip_id = fields.Many2one('stock.picking', string="Transfer Created: ")

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
                    res['bom_products'] = self._calc_bom_products(mo.bom_id, mo.product_qty, show_sublevels)

        default_new_mo_items = self.env.context.get('default_new_mo_items')
        if default_new_mo_items:
            res['new_mo_ids'] = self.env['mrp.production'].browse(default_new_mo_items)

        res = self._convert_to_write(res)
        return res

    def _calc_bom_products(self, bom_id, mo_qty, show_sublevels):
        starting_factor = bom_id.product_uom_id._compute_quantity(
            bom_id.product_qty, bom_id.product_tmpl_id.uom_id, round=False
        )
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

                # search prod in prod_list and add up mo_required_qty if found
                prod_in_list = self.search_product_from_list(prod.id, prod_list)
                if prod_in_list:
                    prod_in_list['mo_required_qty'] += required_qty
                    prod_in_list['adjusted_qty'] = prod_in_list['mo_required_qty']
                else:
                    prod.get_wip_qty()
                    prod.get_stock_qty()
                    prod_list.append([0, 0, {
                        'production_id': self.id,
                        'product_id': prod.id,
                        'part_number': prod.default_code,
                        'product_name': prod.name,
                        'stock_qty': prod.flsp_stock_qty,
                        'wip_qty': prod.flsp_wip_qty,
                        'mo_required_qty': required_qty,
                        'adjusted_qty': required_qty,
                        'bom_level': total_qty['level'],
                    }])
        return prod_list

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

        count_products = 0
        for prod in targetProd:
            _logger.info("---------------------------------Checkin Product ----------------------------->:")
            _logger.info("Product name: "+prod.product_id.name)
            _logger.info("product_id: "+str(prod.product_id.id))
            _logger.info("product_uom: "+str(prod.product_id.uom_id.id))
            _logger.info("product_uom_qty: "+str(prod.adjusted_qty))
            _logger.info("location_id: "+str(picking_type_id.default_location_src_id.id))
            _logger.info("location_dest_id: "+str(picking_type_id.default_location_dest_id.id))
            count_products += 1

        if count_products > 0:
            _logger.info("Creating the transfer")
            create_val = {
                'origin': self.mo_id.name+'WIP-TRANSFER',
                'picking_type_id': picking_type_id.id,
                'location_id': picking_type_id.default_location_src_id.id,
                'location_dest_id': picking_type_id.default_location_dest_id.id,
                'flsp_mo_wip_id': self.mo_id.id,
            }
            _logger.info("Transfer READY ----------------------------->:")
            _logger.info("origin: "+self.mo_id.name+'WIP-TRANSFER')
            _logger.info("picking_type_id: "+str(picking_type_id.id))
            _logger.info("location_id: "+str(picking_type_id.default_location_src_id.id))
            _logger.info("location_dest_id: "+str(picking_type_id.default_location_dest_id.id))
            _logger.info("scheduled_date: "+str(date_start))
            _logger.info("flsp_mo_wip_id: "+str(self.mo_id.id))
            stock_picking = self.env['stock.picking'].create(create_val)
            _logger.info("Transfer created: "+stock_picking.name)

            if stock_picking:

                for prod in targetProd:
                    _logger.info("---------------------------------Creating Stock Move ----------------------------->:")
                    _logger.info("Product name: "+prod.product_id.name)
                    _logger.info("product_id: "+str(prod.product_id.id))
                    _logger.info("product_uom: "+str(prod.product_id.uom_id.id))
                    _logger.info("product_uom_qty: "+str(prod.adjusted_qty))
                    _logger.info("location_id: "+str(picking_type_id.default_location_src_id.id))
                    _logger.info("location_dest_id: "+str(picking_type_id.default_location_dest_id.id))
                    stock_move = self.env['stock.move'].create({
                        'name': prod.product_id.name,
                        'product_id': prod.product_id.id,
                        'product_uom': prod.product_id.uom_id.id,
                        'product_uom_qty': prod.adjusted_qty,
                        'picking_id': stock_picking.id,
                        'location_id': picking_type_id.default_location_src_id.id,
                        'location_dest_id': picking_type_id.default_location_dest_id.id,
                    })
                    _logger.info("Line created:"+stock_move.name)

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
    product_id = fields.Many2one('product.product', string='Product')
    part_number = fields.Char(related='product_id.default_code')
    product_name = fields.Char(related='product_id.name')
    stock_qty = fields.Float('Stock Qty', default=0.0, digits='Product Unit of Measure', readonly=True)
    wip_qty = fields.Float('WIP Qty', default=0.0, digits='Product Unit of Measure', readonly=True)
    mo_required_qty = fields.Float('Required Qty', default=0.0, digits='Product Unit of Measure', readonly=True)
    adjusted_qty = fields.Float('Adjusted Qty', default=0.0, digits='Product Unit of Measure', required=True)
    bom_level = fields.Integer(string="BOM Level")
    flsp_sd_location = fields.Many2one('stock.location', string='Standard Location', related='product_id.flsp_sd_location')
