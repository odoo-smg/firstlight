# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo import tools

class FlspBomAvailabilityView(models.Model):
    """
        Class_Name: FlspBomAvailabilityView
        Model_Name: flsp.bom.availability
        Purpose:    To create a form view based off the wizard results
        Date:       March/1st/2021/M
        Author:     Sami Byaruhanga
        Note:       Functions and code are depicted from FLSPCOMPAREBOM Model
    """

    _name = 'flsp.bom.availability.view'
    _auto = False
    _rec_name = 'bom'
    _description = 'FLSP BoM Availability View'

    # BoM header information
    bom = fields.Many2one('mrp.bom', string='BOM', required=True, ondelete='cascade')
    code = fields.Char('Reference', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product template', readonly=True)
    product_qty = fields.Float(string='BoM Quantity', readonly=True)
    version = fields.Float(string='Version', readonly=True)
    active = fields.Boolean(string='Active')
    product_uom_id = fields.Many2one('uom.uom', 'Product UoM', readonly=True)

    onhand_qty = fields.Float(string='On Hand Qty', readonly=True)
    outgoing_qty = fields.Float(string='Out going qty', readonly=True)
    incoming_qty = fields.Float(string='Incoming Qty', readonly=True)
    forecast_qty = fields.Float(string='Forecast Qty', compute='calculate_forecast_qty', readonly=True)
    bom_line = fields.One2many('flsp.bom.availability.line', 'order_id', string='Order Lines', copy=True, nauto_join=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'flsp_bom_availability_view')
        query = """
        CREATE or REPLACE VIEW flsp_bom_availability_view AS (
        SELECT		    
                    1 as id,
                    mb1.id as bom, mb1.code as code, mb1.product_tmpl_id as product_tmpl_id,
--                    pp.id, 
                    (select sum(quantity) from stock_quant as sq
                        inner join 	stock_location as sl
                        on			sq.location_id = sl.id
                        where 		sl.usage='internal'
                        group by    product_id 
                    having product_id = pp.id) as onhand_qty,
                    
                    (select 		sum(sm.product_uom_qty) from stock_move as sm
                        inner join	stock_picking as sp
                        on			sm.picking_id = sp.id
                        where 		sp.name like '%OUT%'
                        group by	product_id
                    having 		product_id=pp.id) as outgoing_qty,
                    
                    (select 		sum(sm.product_uom_qty) from stock_move as sm
                        inner join	stock_picking as sp
                        on			sm.picking_id = sp.id
                        where 		sp.name like '%IN%'
                        group by	product_id
                    having 		product_id=pp.id) as incoming_qty,
                    
                    mb1.product_qty as product_qty, mb1.product_uom_id as product_uom_id, mb1.version as version, mb1.active as active
        FROM 		mrp_bom as mb1
        inner join	product_template as pt
        on			mb1.product_tmpl_id = pt.id
        inner join 	product_product as pp
        on 			pt.id = pp.product_tmpl_id
        where 		mb1.id = (select bom from flsp_bom_availability order by id desc limit 1)
        );
        """
        self.env.cr.execute(query)

    def calculate_forecast_qty(self):
        """
            Purpose: to compute the forecast qty
        """
        self.write({'forecast_qty': self.product_tmpl_id.virtual_available})

    class FlspBomAvailability(models.Model):
        """
            Purpose to hold the bom values
        """
        _name = 'flsp.bom.availability'

        bom = fields.Many2one('mrp.bom', string='BoM', required=True, ondelete='cascade')

class FlspBomAvailabilityLine(models.Model):
    """
        Purpose: To get the bom line information to be used in a one to one field
    """
    _name = 'flsp.bom.availability.line'
    _auto = False

    order_id = fields.Many2one('flsp.bom.availability.view', string='Reference', required=True, ondelete='cascade', index=True, copy=False)
    id1 = fields.Float(string='BOM', readonly=True)
    product_line_id = fields.Many2one('product.product', string='BOM component', readonly=True)
    product_line_qty = fields.Float(string='BOM required qty', readonly=True)
    uom_id = fields.Many2one('uom.uom', 'UoM', readonly=True)
    onhand_qty_line = fields.Float(string='On Hand Qty', readonly=True)
    outgoing_qty_line = fields.Float(string='Outgoing Qty', readonly=True)
    incoming_qty_line = fields.Float(string='Incoming Qty', readonly=True)
    forecast_qty_line = fields.Float(string='Forecast Qty', compute='calculate_forecast_qty_line', readonly=True)

    def init(self):
        query = """
        CREATE or REPLACE VIEW flsp_bom_availability_line AS (
        SELECT
                row_number() OVER() AS id,
                1 as order_id ,
                mbl1.bom_id as id1, mbl1.product_id as product_line_id, mbl1.product_qty as product_line_qty, mbl1.product_uom_id as uom_id,
                (select sum(quantity) from stock_quant as sq
                inner join 	stock_location as sl
                on			sq.location_id = sl.id
                where 		sl.usage='internal'
                group by product_id 
                having product_id = mbl1.product_id) as onhand_qty_line,
                
                (select 		sum(sm.product_uom_qty) from stock_move as sm
                    inner join	stock_picking as sp
                    on			sm.picking_id = sp.id
                    where 		sp.name like '%OUT%'
                    group by	product_id
                having 		product_id= mbl1.product_id) as outgoing_qty_line,
                
                (select 		sum(sm.product_uom_qty) from stock_move as sm
                    inner join	stock_picking as sp
                    on			sm.picking_id = sp.id
                    where 		sp.name like '%IN%'
                    group by	product_id
                having 		product_id= mbl1.product_id) as incoming_qty_line
                      
        FROM    (select * from mrp_bom_line where bom_id=(select bom from flsp_bom_availability order by id desc limit 1)) as mbl1
        );
        """
        self.env.cr.execute(query)

    def calculate_forecast_qty_line(self):
        """
            Purpose: to compute the forecast qty
        """
        self.forecast_qty_line = 0
        for line1 in self:
            for line2 in self.product_line_id:
                if line1.product_line_id == line2:
                    line1.forecast_qty_line = line2.product_tmpl_id.virtual_available