# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError


class FlspBomAvailabilityLine(models.Model):
    """
        Class name: FlspBomAvailabilityLine
        model name: flsp.bom.availability.line
        Purpose:    To get the bom line information to be used in a one to one field
    """
    _name = 'flsp.bom.availability.line'
    _description = "FLSP BOM Availability for BOM Line"
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
    comp_on_demand = fields.Float(string="Compute On Demand", compute="compute_on_demand")
    reserved = fields.Float(string="Reserved Qty", compute='compute_qty')
    stock_qty = fields.Float(string="Stock Qty", compute='compute_qty')
    wip_qty = fields.Float(string="WIP Qty", compute='compute_qty')
    mo_qty = fields.Float(string="MO Qty", compute='compute_qty')

    def compute_on_demand(self):
        for line in self:
            latest_calc = line.env['flsp.purchase.mrp'].search(['&', ('create_uid','=',2), ('state','=','done')], order='date desc', limit=1)
            mrp_line = line.env['flsp.purchase.mrp.line'].search(['&', ('purchase_mrp_id','=',latest_calc.id), ('product_tmpl_id','=', line.product_line_id.product_tmpl_id.id)])
            line.comp_on_demand = mrp_line.open_demand


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
                                left join	(
												select lin, id, sequence, product_tmpl_id from (
												select row_number() OVER(PARTITION BY product_tmpl_id order by sequence) AS lin, id, sequence, product_tmpl_id  from mrp_bom where active = true  order by product_tmpl_id
												) B1 where lin = 1

								) as mb
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
						left join	(
										select lin, id, sequence, product_tmpl_id from (
										select row_number() OVER(PARTITION BY product_tmpl_id order by sequence) AS lin, id, sequence, product_tmpl_id  from mrp_bom where active = true  order by product_tmpl_id
										) B1 where lin = 1

						) as mb
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
        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')]).parent_path
        if not pa_location:
            raise UserError('WIP Stock Location is missing')
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location + '%')]).ids
        if not pa_wip_locations:
            raise UserError('WIP Stock Location is missing')

        for line in self:
            line.onhand_qty_line = line.product_line_id.qty_available
            line.forecast_qty_line = line.product_line_id.virtual_available
            reserved = 0
            stock_quants = self.env['stock.quant'].search([('product_id', '=', line.product_line_id.id)])
            for stock_quant in stock_quants:
                if stock_quant.location_id.usage == 'internal':
                    reserved += stock_quant.reserved_quantity
            line.reserved = reserved
            pa_wip_qty = 0
            stock_quant = self.env['stock.quant'].search(
                ['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', line.product_line_id.id)])
            for stock_lin in stock_quant:
                pa_wip_qty += stock_lin.quantity

            line.wip_qty = pa_wip_qty
            line.stock_qty = line.product_line_id.qty_available - pa_wip_qty

            open_mos = self.env['mrp.production'].search([('state', 'in', ('to_close', 'progress', 'confirmed'))])
            mo_qty = 0
            for mo in open_mos:
                if mo.product_id.id == line.product_line_id.id:
                    mo_qty += mo.product_qty
                else:
                    for mo_line in mo.move_raw_ids:
                        if mo_line.product_id.id == line.product_line_id.id:
                            mo_qty += mo_line.product_uom_qty
            line.mo_qty = mo_qty

    class FlspBomAvailability(models.Model):
        """
            Purpose to hold the bom values
        """
        _name = 'flsp.bom.availability'
        _description = "FLSP BOM Availability"
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
