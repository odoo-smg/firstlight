# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, datetime
import logging
_logger = logging.getLogger(__name__)

class FlspMOProduct(models.TransientModel):
    _name = 'flspmrp.mo.product'
    _description = "Product in the BoM structure for a MO"

    selected = fields.Boolean('Selected')
    production_id = fields.Many2one('flspmrp.bom.structure', required=True, check_company=True)
    product_id = fields.Many2one('product.product', string='Product', required=True, check_company=True)
    part_number = fields.Char(related='product_id.default_code')
    name = fields.Char(related='product_id.name')
    stock_qty = fields.Float('Stock Qty', default=0.0, digits='Product Unit of Measure', readonly=True, required=True) 
    wip_qty = fields.Float('WIP Qty', default=0.0, digits='Product Unit of Measure', readonly=True, required=True)
    forecasted_qty = fields.Float(related='product_id.virtual_available', string='Forecasted Qty') 
    available_qty = fields.Float('Available Qty', default=0.0, digits='Product Unit of Measure', required=True)
    mo_required_qty = fields.Float('Required Qty', default=0.0, digits='Product Unit of Measure', readonly=True, required=True)
    adjusted_qty = fields.Float('Adjusted Qty', default=0.0, digits='Product Unit of Measure', required=True)


class FlspMrpBomStructure(models.TransientModel):
    _name = 'flspmrp.bom.structure'
    _description = "Wizard: Display products in the BoM structure for the MO"
    
    mo_id = fields.Many2one('mrp.production', string="MO", required=True)
    mo_name = fields.Char(related='mo_id.name', string="MO name", readonly=True)
    bom_id = fields.Many2one(related='mo_id.bom_id', string="Bill of Material", readonly=True)
    bom_products = fields.One2many(comodel_name='flspmrp.mo.product', inverse_name='production_id', string="products in BoM structure")
    new_mo_ids = fields.One2many(comodel_name='mrp.production', inverse_name='id', string="New MOs")
        
    @api.model
    def default_get(self, fields):
        res = super(FlspMrpBomStructure, self).default_get(fields)
        default_mo_id = self.env.context.get('default_mo_id')
        if default_mo_id:
            mo = self.env['mrp.production'].browse(default_mo_id)
            if mo.exists():
                res['mo_id'] = mo.id
                if 'mo_name' in fields:
                    res['mo_name'] = mo.name
                if 'bom_id' in fields:
                    res['bom_id'] = mo.bom_id
                if 'bom_products' in fields:
                    res['bom_products'] = self._calc_bom_products(mo.bom_id, mo.product_qty)
                            
        default_new_mo_items = self.env.context.get('default_new_mo_items')
        if default_new_mo_items:
            res['new_mo_ids'] = self.env['mrp.production'].browse(default_new_mo_items)
            
        res = self._convert_to_write(res)
        return res

    def _calc_bom_products(self, bom_id, mo_qty):
        starting_factor = bom_id.product_uom_id._compute_quantity(
                bom_id.product_qty, bom_id.product_tmpl_id.uom_id, round=False
            )
        totals = bom_id._get_flattened_totals(factor=starting_factor)

        # retrieve the product ids from the list
        prod_list = []
        route_mfg = self.env.ref('mrp.route_warehouse0_manufacture').id
        for order, total_qty in totals.items():
            # EXAMPLE of totals: {'total': 1.0, 'level': 1, 'bom': '20201029195521', 'bom_plm': True, 'type':normal, 'track': 'lot', 'prod': product.product(1015,)}
            if (not total_qty['prod']) or (not total_qty['type']):
                continue
            
            if (
                (
                    (not 'flsp_backflush' in self.env['product.template']._fields) 
                    or 
                    (('flsp_backflush' in self.env['product.template']._fields) and total_qty['prod'].flsp_backflush == False)
                )
                and route_mfg in total_qty['prod'].route_ids.ids 
                and total_qty['type'] == 'normal'
                ):
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
                    prod.get_available_qty()
                    prod_list.append([0, 0, {
                                    'production_id': self.id,
                                    'product_id': prod.id, 
                                    'part_number': prod.default_code,
                                    'name': prod.name,
                                    'stock_qty': prod.flsp_stock_qty,
                                    'wip_qty': prod.flsp_wip_qty,
                                    'forecasted_qty': prod.virtual_available,
                                    'available_qty': prod.flsp_available_qty,
                                    'mo_required_qty': required_qty,
                                    'adjusted_qty': required_qty,
                                }])
        
        return prod_list
    
    def search_product_from_list(self, id, prod_list):
        for prod_entry in prod_list:
            if id == prod_entry[2]['product_id']:
                return prod_entry[2]
        
        return False

    def button_create_mo(self):
        self.ensure_one()
        
        for prod in self.bom_products:
            prod.write({'production_id': self.id})
        
        targetProd = self.env['flspmrp.mo.product'].search(['&', ('production_id', '=',  self.id), ('selected', '=', True)])
        
        new_mos = []
        for prod in targetProd:
            new_mo = self.create_mo(prod)
            new_mos.append(new_mo.id)
            
        return {
            'name': 'MO Creation',
            'view_mode': 'form',
            'view_id': self.env.ref('flsp-mrp.flsp_mrp_message_form_view').id,
            'res_model': 'flspmrp.bom.structure',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_mo_id': self.mo_id.id,
                'default_new_mo_items': new_mos,
            }
        }

    def create_mo(self, prod):
        date_start = datetime.now().today() + timedelta(days=1)
        date_parent_start = self.mo_id.date_planned_start
        if date_parent_start:
            date_start = date_parent_start + timedelta(days=-1)
        date_end = date_start + timedelta(hours=4)
        
        bom = self.get_bom(prod, self.mo_id)
        picking_type_id = self.get_picking_type(bom, self.mo_id)
        
        new_mo = self.env['mrp.production'].create({
            'product_id': prod.product_id.id,  
            'product_qty': prod.adjusted_qty,
            'product_uom_id': prod.product_id.uom_id.id,
            'date_planned_start': date_start,
            'date_planned_finished': date_end,
            'user_id': self.mo_id.user_id.id,
            'origin': self.mo_id.name,
            'bom_id': bom.id,
            'picking_type_id': picking_type_id.id,
        })
        
        # update 'location_src_id' and 'location_dest_id' after MO's creation because the process depends on the MO's attributes
        self.set_locations(new_mo)

        # update 'product_list' after MO's creation because the process depends on the MO's attributes
        # this method must be called AFTER set_locations() above because location from the new MO is required by the bom products
        self.set_bom_product(new_mo)
        
        return new_mo
    
    def get_bom(self, prod, mo_id):
        # copy from onchange_product_id() in model 'mrp.production'
        return self.env['mrp.bom']._bom_find(product=prod.product_id, picking_type=mo_id.picking_type_id, company_id=mo_id.company_id.id, bom_type='normal')
    
    def get_picking_type(self, bom_id, mo_id):
        # copy from _onchange_bom_id() in model 'mrp.production'
        return bom_id.picking_type_id or mo_id.picking_type_id
    
    def set_bom_product(self, new_mo):
        # call _onchange_move_raw() in model 'mrp.production' 
        new_mo._onchange_move_raw()
    
    def set_locations(self, new_mo):
        # call onchange_picking_type() in model 'mrp.production' 
        new_mo.onchange_picking_type()
        