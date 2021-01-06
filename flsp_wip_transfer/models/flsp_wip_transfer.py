# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime

class FlspMrpPlanningLine(models.Model):
    _name = 'flsp.wip.transfer'
    _description = 'FLSP Weekly Transfer'

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
    stock_move_id = fields.Many2one('stock.move', string='Move Line Id', readonly=True)

    def _flsp_calc_demands(self, days_ahead):

        cur_date = datetime.datetime.now().date()
        date_mo = (cur_date + relativedelta(days=+ days_ahead))

        production_orders = self.env['mrp.production'].search(
            ['&', ('state', 'not in', ['done', 'cancel', 'draft']), ('date_planned_start', '<=', date_mo)])


        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')]).parent_path
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location+'%')]).ids

        ## Remove production orders done:
        wip_transfers = self.env['flsp.wip.transfer'].search([('state', '=', ['transfer'])])

        for wip_trans in wip_transfers:
            delete_wip = True
            for production in production_orders:
                if wip_trans.source == production.name:
                    delete_wip = False
            if delete_wip:
                wip_trans.unlink()

        for production in production_orders:
            components = self._get_flattened_totals(production.bom_id, production.product_qty)
            for prod in components:
                wip_trans = self.env['flsp.wip.transfer'].search(['&', ('source', '=', production.name), ('product_id', '=', prod.id)])
                stock_quant = self.env['stock.quant'].search(['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', prod.id)])
                pa_wip_qty = 0
                for stock_lin in stock_quant:
                    pa_wip_qty += stock_lin.quantity
                if wip_trans:
                    #update current
                    wip_trans.mfg_demand = components[prod]['total']
                    wip_trans.suggested = 1
                    wip_trans.adjusted = components[prod]['total']
                    wip_trans.stock_qty = prod.qty_available - pa_wip_qty
                    wip_trans.pa_wip_qty = pa_wip_qty
                else:
                    #insert new
                    wip = self.env['flsp.wip.transfer'].create({
                        'description': prod.name,
                        'default_code': prod.default_code,
                        'product_id': prod.id,
                        'stock_qty': prod.qty_available - pa_wip_qty,
                        'pa_wip_qty': pa_wip_qty,
                        'source': production.name,
                        'mfg_demand': components[prod]['total'],
                        'suggested': 1,
                        'adjusted': components[prod]['total'],
                        'state': 'transfer',
                        'production_id': production.id,
                    })
        return

    def _get_flattened_totals(self, bom, factor=1, totals=None, level=None):
        """Calculate the **unitary** product requirements of flattened BOM.
        *Unit* means that the requirements are computed for one unit of the
        default UoM of the product.
        :returns: dict: keys are components and values are aggregated quantity
        in the product default UoM.
        """
        if level is None:
            level = 1
        if totals is None:
            totals = {}
        factor /= bom.product_uom_id._compute_quantity(
            bom.product_qty, bom.product_tmpl_id.uom_id, round=False
        )
        for line in bom.bom_line_ids:
            sub_bom = bom._bom_find(product=line.product_id)
            if sub_bom:
                new_factor = factor * line.product_uom_id._compute_quantity(
                    line.product_qty, line.product_id.uom_id, round=False
                )
                '''if totals.get(line.product_id):
                    totals[line.product_id]['total'] += (
                        factor
                        * line.product_uom_id._compute_quantity(
                            line.product_qty, line.product_id.uom_id, round=False
                        )
                    )
                else:
                    totals[line.product_id] = {'total':(
                        factor
                        * line.product_uom_id._compute_quantity(
                            line.product_qty, line.product_id.uom_id, round=False
                        )
                    ), 'level': level, 'bom': sub_bom.code}
                '''
                level += 1
                self._get_flattened_totals(sub_bom, new_factor, totals, level)
                level -= 1
            else:
                if totals.get(line.product_id):
                    totals[line.product_id]['total'] += (
                        factor
                        * line.product_uom_id._compute_quantity(
                            line.product_qty, line.product_id.uom_id, round=False
                        )
                    )
                else:
                    totals[line.product_id] = {'total':(
                        factor
                        * line.product_uom_id._compute_quantity(
                            line.product_qty, line.product_id.uom_id, round=False
                        )
                    ), 'level': level, 'bom': ''}
        return totals
