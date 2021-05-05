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
    product_name = fields.Char(related='product_id.name')
    stock_qty = fields.Float('Stock Qty', default=0.0, digits='Product Unit of Measure', readonly=True, required=True) 
    wip_qty = fields.Float('WIP Qty', default=0.0, digits='Product Unit of Measure', readonly=True, required=True)
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
        _logger.info("default_mo_id: " + str(default_mo_id))
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
        _logger.info("default_new_mo_items: " + str(default_new_mo_items))
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

        for order, total_qty in totals.items():
            # {'total': 1.0, 'level': 1, 'bom': '', 'bom_plm': '', 'track': 'lot', 'prod': product.product(1015,)}
            if total_qty['bom'] and ('flsp_backflush' in self.env['product.template']._fields) and total_qty['prod'].flsp_backflush == False:
                # add product in the list
                prod = total_qty['prod']
                prod.get_wip_qty()
                prod.get_stock_qty()
                mo_required_qty = mo_qty * total_qty['total']
                prod_list.append([0, 0, {
                                'production_id': self.id,
                                'product_id': prod.id, 
                                'part_number': prod.default_code,
                                'product_name': prod.name,
                                'stock_qty': prod.flsp_stock_qty,
                                'wip_qty': prod.flsp_wip_qty,
                                'mo_required_qty': mo_required_qty,
                                'adjusted_qty': mo_required_qty,
                            }])
        return prod_list

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
        date_now = datetime.now()
        date_start = date_now.today() + timedelta(days=1)
        date_end = date_now.today() + timedelta(days=15)
        
        bom = self.env['mrp.bom']._bom_find(product=prod.product_id, picking_type=self.mo_id.picking_type_id, company_id=self.mo_id.company_id.id, bom_type='normal')
        
        new_mo = self.env['mrp.production'].create({
            'product_id': prod.product_id.id,  
            'product_qty': prod.adjusted_qty,
            'date_planned_finished': date_end,
            'date_planned_start': date_start,
            'user_id': self.mo_id.user_id.id,
            'origin': self.mo_id.name,
            'product_uom_id': prod.product_id.uom_id.id,
            'bom_id': bom.id,
        })
        
        return new_mo