# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api
from datetime import datetime
from odoo.exceptions import UserError


class Flspwipview(models.Model):
    _name = 'flsp.wip.view'
    _auto = False
    _description = 'WIP Transfer'

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product template', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    stock_qty = fields.Float(string='WH/Stock', readonly=True)
    pa_wip_qty = fields.Float(string='PA/WIP', readonly=True)
    source = fields.Char("MO", readonly=True)
    mfg_demand = fields.Float(string='Qty', readonly=True)
    suggested = fields.Float(string='Suggested', readonly=True)
    adjusted = fields.Float(string='Adjusted')
    state = fields.Selection([
        ('transfer', 'to transfer'),
        ('short', 'not available'),
        ('done', 'done'),
    ], string='State', readonly=True)
    stock_picking = fields.Many2one('stock.picking', string='Stock Picking', readonly=False)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', readonly=False)
    qty_items = fields.Integer('Items')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'flsp_wip_view')

        query = """
        CREATE or REPLACE VIEW flsp_wip_view AS (
        SELECT
        max(id) as id,
        max(description) as description,
        max(default_code) as default_code,
        max(product_tmpl_id) as product_tmpl_id,
        product_id,
        max(stock_qty) as stock_qty,
        max(pa_wip_qty) as pa_wip_qty,
        max(source) as source,
        sum(mfg_demand) as mfg_demand,
        sum(suggested) as suggested,
        sum(adjusted) as adjusted,
        max(state) as state,
        max(stock_picking) as stock_picking,
        max(production_id) as production_id,
        count(id) as qty_items
        FROM flsp_wip_transfer
        where state != 'done'
        group by product_id 
        );
        """
        self.env.cr.execute(query)

    def name_get(self):
        return [(record.id, record.product_id.name) for record in self]

    def execute_suggestion(self):
        move_lines = []
        wip_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA/WIP')])
        stock_location = self.env['stock.location'].search([('complete_name', '=', 'WH/Stock')])
        stock_picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'INT')])
        if not stock_picking_type:
            raise UserError('Picking type Internal is missing')
        if not wip_location:
            raise UserError('WIP Stock Location is missing')
        if not stock_location:
            raise UserError('Stock Location is missing')
        count_products = 0
        for product in self:
            count_products += 1

        if count_products > 0:
            create_val = {
                'origin': 'FLSP-WIP-TRANSFER',
                'picking_type_id': stock_picking_type.id,
                'location_id': stock_location.id,
                'location_dest_id': wip_location.id,
            }
            stock_picking = self.env['stock.picking'].create(create_val)

            for product in self:

                print(product.product_id.name+' qty: '+str(product.adjusted))

                move_line = self.env['stock.move'].create({
                    'name': product.product_id.name,
                    'product_id': product.product_id.id,
                    'product_uom': product.product_id.uom_id.id,
                    'product_uom_qty': product.adjusted,
                    #'product_qty': product.adjusted,
                    'picking_id': stock_picking.id,
                    'location_id': stock_location.id,
                    'location_dest_id': wip_location.id
                })
                wip_transfer = self.env['flsp.wip.transfer'].search(['&',('product_id', '=', product.product_id.id), ('state', '!=', 'done')])
                for wip_line in wip_transfer:
                    wip_line.state = "done"
                    wip_line.stock_picking = stock_picking.id
                    wip_line.stock_move_id = move_line.id
            stock_picking.action_confirm()

            self.env['flspautoemails.bpmemails'].send_email(stock_picking, 'WIP001')

        return

    def action_open_wip_transfer(self):
        self.ensure_one()
        action = self.env.ref('flsp_wip_transfer.flsp_wip_transfer_action').read()[0]
        action['domain'] = ['&', ('product_id', '=', self.product_id.id), ('state', '!=', 'done')]
        #action['domain'] = [('product_id', '=', self.product_id.id)]
        return action
