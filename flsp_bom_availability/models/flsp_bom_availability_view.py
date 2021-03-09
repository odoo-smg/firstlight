# -*- coding: utf-8 -*-
from odoo import models, fields

class FlspBomAvailabilityLine(models.Model):
    """
        Class name: FlspBomAvailabilityLine
        model name: flsp.bom.availability.line
        Purpose:    To get the bom line information to be used in a one to one field
    """
    _name = 'flsp.bom.availability.line'
    _auto = False
    _order = 'bom_level asc'

    id1 = fields.Float(string='BOM', readonly=True)
    product_line_id = fields.Many2one('product.product', string='BOM component', readonly=True)
    product_line_qty = fields.Float(string='BOM qty', readonly=True)
    bom_line_id = fields.Many2one('mrp.bom', string='Parent Bom_id')
    bom_comp_id = fields.Many2one('mrp.bom', string='Component bom_id')
    bom_level = fields.Integer(string='Bom level')
    uom_id = fields.Many2one('uom.uom', 'UoM', readonly=True)
    has_bom = fields.Boolean(string='Has BOM', compute='compute_has_bom')
    onhand_qty_line = fields.Float(string='OnHand Qty', compute='compute_qty')
    forecast_qty_line = fields.Float(string='Forecast Qty', compute='compute_qty')

    def init(self):
        query = """
        CREATE or REPLACE VIEW flsp_bom_availability_line AS (
        with recursive explode_bom1 as(
            select 	        product_id, product_qty, mbl_bom_id, name, bom_id, 1 as level, product_uom_id
                from 		(select 		mbl.product_id, mbl.product_qty, mbl.bom_id as mbl_bom_id, --pp.default_code, 
                                            pt.id, pt.name ,mb.id as bom_id, mbl.product_uom_id
                                from		mrp_bom_line mbl
                                inner join 	product_product as pp
                                on			mbl.product_id = pp.id
                                inner join 	product_template as pt
                                on 			pp.product_tmpl_id = pt.id
                                full join	mrp_bom as mb
                                on 			pt.id = mb.product_tmpl_id) as table1
                where mbl_bom_id = (select bom from flsp_bom_availability order by id desc limit 1)
                         
            union -- recursive part now 
                select 		r.product_id, r.product_qty, r.mbl_bom_id, r.name, r.bom_id, eb.level+1 as level, 
                            r.product_uom_id
                from 		(select 		mbl.product_id, mbl.product_qty, mbl.bom_id as mbl_bom_id, --pp.default_code, 
                        pt.id, pt.name ,mb.id as bom_id, mbl.product_uom_id
                        from		mrp_bom_line mbl
                        inner join 	product_product as pp
                        on			mbl.product_id = pp.id
                        inner join 	product_template as pt
                        on 			pp.product_tmpl_id = pt.id
                        full join	mrp_bom as mb
                        on 			pt.id = mb.product_tmpl_id) as r
                inner join	explode_bom1 eb on eb.bom_id = r.mbl_bom_id
        ) 
        
        -- Getting the top level main component 
        select      1000000 AS id,
                    mb.id as id1,
                    pp.id as product_line_id, 
                    mb.product_qty as product_line_qty, 
                    mb.id as bom_line_id, 
                    mb.id as bom_comp_id, 
                    0 as bom_level, 
                    mb.product_uom_id as uom_id
        from        mrp_bom as mb
        inner join  product_template as pt
        on          mb.product_tmpl_id = pt.id
        inner join  product_product as pp
        on          pt.id = pp.product_tmpl_id
        where       mb.id = (select bom from flsp_bom_availability order by id desc limit 1)
        union 
        
        --this is where we use the recursive table in the database 
        select    row_number() OVER() AS id,
                    bom_id as id1 ,
                    product_id as product_line_id, product_qty as product_line_qty,
                    mbl_bom_id as bom_line_id,
                    bom_id as bom_comp_id,
                    level as bom_level,
                    product_uom_id as uom_id
                from explode_bom1
        );
        """
        self.env.cr.execute(query)

    def compute_has_bom(self):
        self.has_bom = False
        for line in self:
            if line.bom_comp_id:
                line.has_bom = True

    def compute_qty(self):
        for line in self:
            line.onhand_qty_line = line.product_line_id.qty_available
            line.forecast_qty_line = line.product_line_id.virtual_available

    class FlspBomAvailability(models.Model):
        """
            Purpose to hold the bom values
        """
        _name = 'flsp.bom.availability'
        _rec_name = 'bom'

        bom = fields.Many2one('mrp.bom', string='BoM', required=True, ondelete='cascade')

"""
    --***************RECURSIVE Explode for boms with subqueries******************************
        with recursive explode_bom1 as(
            select 			product_id, product_qty, mbl_bom_id, name, bom_id, 1 as level
                from 		(select 		mbl.product_id, mbl.product_qty, mbl.bom_id as mbl_bom_id, --pp.default_code, 
                        pt.id, pt.name ,mb.id as bom_id
            from		mrp_bom_line mbl
            inner join 	product_product as pp
            on			mbl.product_id = pp.id
            inner join 	product_template as pt
            on 			pp.product_tmpl_id = pt.id
            full join	mrp_bom as mb
            on 			pt.id = mb.product_tmpl_id) as table1
                where 		mbl_bom_id=2
            
            union -- recursive part now 
                select 		r.product_id, r.product_qty, r.mbl_bom_id, r.name, r.bom_id, eb.level + 1 AS level
                from 		(select 		mbl.product_id, mbl.product_qty, mbl.bom_id as mbl_bom_id, --pp.default_code, 
                        pt.id, pt.name ,mb.id as bom_id
            from		mrp_bom_line mbl
            inner join 	product_product as pp
            on			mbl.product_id = pp.id
            inner join 	product_template as pt
            on 			pp.product_tmpl_id = pt.id
            full join	mrp_bom as mb
            on 			pt.id = mb.product_tmpl_id) as r
                inner join	explode_bom1 eb on eb.bom_id = r.mbl_bom_id
        ) select *	from explode_bom1;
    --***************RECURSIVE Explode for boms**********************************************
        with recursive explode_bom as(
            select 			product_id, product_qty, mbl_bom_id, name, bom_id, 1 as level
                from 		refined_table
                where 		mbl_bom_id=2
            
            union -- recursive part now 
                select 		r.product_id, r.product_qty, r.mbl_bom_id, r.name, r.bom_id, eb.level + 1 AS level
                from 		refined_table as r
                inner join	explode_bom eb on eb.bom_id = r.mbl_bom_id
        ) select *	from explode_bom;
        
        select * from temp
        select * from refined_table
        
        create table refined_table as
            select 		mbl.product_id, mbl.product_qty, mbl.bom_id as mbl_bom_id, --pp.default_code, 
                        pt.id, pt.name ,mb.id as bom_id
            from		mrp_bom_line mbl
            inner join 	product_product as pp
            on			mbl.product_id = pp.id
            inner join 	product_template as pt
            on 			pp.product_tmpl_id = pt.id
            full join	mrp_bom as mb
            on 			pt.id = mb.product_tmpl_id
        --where 		mbl.bom_id = 2
        
        select		mb.id, mb.code, mb.product_tmpl_id, mb.product_qty,mbl.product_id as comp	
            from 		mrp_bom as mb
            inner join	mrp_bom_line as mbl
            on			mbl.bom_id = mb.id
            where 		mb.id = 2
        
        create table temp as --will replace with subquery
            select 		mbl.product_id, mbl.product_qty, mbl.bom_id as mbl_bom_id, --pp.default_code, 
                        pt.id, pt.name ,mb.id as bom_id
            from		mrp_bom_line mbl
            inner join 	product_product as pp
            on			mbl.product_id = pp.id
            inner join 	product_template as pt
            on 			pp.product_tmpl_id = pt.id
            full join	mrp_bom as mb
            on 			pt.id = mb.product_tmpl_id
            where 		mbl.bom_id = 2
    --***************************************************************************************
"""



































