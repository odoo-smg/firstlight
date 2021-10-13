# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models


class FlspCostDetail(models.Model):
    """
        Class_Name: FlspCostDetail
        Model_Name: flsp.cost.detail
        Purpose:    Create a view for Cost Detail Report
        Date:       October/12th/Tuesday/2021
        Updated:
        Author:     Alexandre Sousa
    """
    _name = 'flsp.cost.detail'
    _auto = False
    _description = 'Cost Detail Report'

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')
    date = fields.Datetime(string="Date", readonly=True)
    location_id = fields.Many2one('stock.location', string='Source', readonly=True)
    location_dest_id = fields.Many2one('stock.location', string='Destination', readonly=True)
    reference = fields.Char(string="Reference", readonly=True)
    qty_done = fields.Float(string='Qty Moved', readonly=True)
    price_unit = fields.Float(string='Price Unit', readonly=True)

    product_qty = fields.Float(string='Product Qty', readonly=True)

    value = fields.Float(string='Value', readonly=True)
    unit_cost = fields.Float(string='Unit Cost', readonly=True)

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    #product_uom = fields.Many2one('uom.uom', 'UOM', readonly=True)

    product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)  ###

    balance = fields.Float(string='Balance', readonly=True, compute='_compute_balance_cost')
    cost = fields.Float(string='Unit Cost', readonly=True, compute='_compute_balance_cost', digits='Product Price')

    def _compute_balance_cost(self):
        product = False
        last_balance = False
        last_cost = False
        reg = 1
        for line in self.sorted(key=lambda r: r.date):
            current_balance = 0
            current_cost = 0
            if not product:
                product = line.product_id
            if product == line.product_id:
                if last_balance:
                    current_balance = last_balance

                if line.location_id:
                    if "Virtual" in line.location_id.complete_name \
                            or "Partner" in line.location_id.complete_name \
                            or "Rejected" in line.location_id.complete_name:
                        current_balance += line.qty_done
                if line.location_dest_id:
                    if "Virtual" in line.location_dest_id.complete_name \
                            or "Partner" in line.location_dest_id.complete_name \
                            or "Rejected" in line.location_dest_id.complete_name:
                        current_balance -= line.qty_done
                if last_cost:
                    current_cost = last_cost
                if line.picking_type_id.id != 0:
                    if line.picking_type_id.code != "internal":
                        if last_balance + line.product_qty != 0:
                            current_cost = (last_cost * last_balance) + abs(line.value)
                            current_cost = current_cost / (last_balance + line.product_qty)
                else:
                    if "Product value manually modified" in line.reference:
                        print("-----------------------------------------------------------------------------")
                        print(line.reference)
                        print(line.reference.find(' to '))
                        print(line.reference[line.reference.find(' to ')+4:-1])
                        current_cost = float(line.reference[line.reference.find(' to ')+4:-1])

                line.cost = current_cost
                line.balance = current_balance
                last_balance = current_balance
                last_cost = current_cost
                print('Reg: '+str(reg)+'  Calculating date: ' + str(line.date) + '   cost is: '+str(current_cost) + '    Balance is: '+str(current_balance))
                reg = reg + 1
            product = line.product_id
        return 0

    # pdct_name = fields.Char()###
    # lot_name = fields.Char()###
    # stck_name = fields.Char()###
    # usage_name = fields.Char()###

    def init(self):
        """
            Purpose: To extract database information and create tree view using the query
        """
        tools.drop_view_if_exists(self._cr, 'flsp_cost_detail')

        query = """
        CREATE or REPLACE VIEW flsp_cost_detail AS(
            select      sml.id+1000 as id,
                        sm.picking_type_id,
                        sml.date, sml.location_id, sml.location_dest_id, sml.reference, sml.qty_done, 
                        sm.price_unit, sm.product_qty,
                        svl.value, svl.unit_cost, 
                        sml.product_id, pp.product_tmpl_id
            from		stock_move_line sml
            inner join product_product pp 
            on         pp.id = sml.product_id
            and        pp.active = True
            inner join stock_move sm
            on         sml.move_id = sm.id
            left join  stock_valuation_layer svl
            on         svl.stock_move_id = sm.id 
            left join  stock_picking_type spt
            on         sm.picking_type_id = spt.id
            where      sml.state = 'done'
            union all  
            
            select svl.id, 0 as picking_type_id, svl.create_date as date, null as location_id, null as location_dest_id, description as reference, quantity as qty_done, unit_cost as price_unit, 0, value, unit_cost, product_id, product_tmpl_id 
            from stock_valuation_layer svl
            inner join product_product pp
            on         pp.id = svl.product_id
            where stock_move_id is null
        );
        """
        self.env.cr.execute(query)

