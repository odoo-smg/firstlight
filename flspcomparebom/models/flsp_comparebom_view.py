# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo import tools


class FlspCompareBomView(models.Model):
    """
        Class_Name: FlspCompareBomView
        Model_Name: flsp.comparebom.view
        Purpose:    To create a form view based off the wizard results
        Date:       January/15/2021/F
        Author:     Sami Byaruhanga
    """
    _name = 'flsp.comparebom.view'
    _rec_name = 'page_name'
    _auto = False
    _description = 'FLSP Compare BoM View'

    page_name= fields.Char()

    # BoM header information
    bom1 = fields.Many2one('mrp.bom', string='BOM 1', required=True, ondelete='cascade')
    bom2 = fields.Many2one('mrp.bom', string='BOM 2', required=True, ondelete='cascade')

    code1 = fields.Char('Reference1', readonly=True)
    product_tmpl_id1 = fields.Many2one('product.template', string='Product template1', readonly=True)
    product_qty1 = fields.Float(string='Quantity1', readonly=True)
    version1 = fields.Float(string='Version1', readonly=True)
    active1 = fields.Boolean(string='Active1')
    product_uom_id1 = fields.Many2one('uom.uom', 'Product UoM 1', readonly=True)

    code2 = fields.Char('Reference2', readonly=True)
    product_tmpl_id2 = fields.Many2one('product.template', string='Product template2', readonly=True)
    product_qty2 = fields.Float(string='Quantity2', readonly=True)
    version2 = fields.Float(string='Version2', readonly=True)
    active2 = fields.Boolean(string='Active2')
    product_uom_id2 = fields.Many2one('uom.uom', 'Product UoM 2', readonly=True)

    bom_line = fields.One2many('flsp.comparebom.line', 'order_id', string='Order Lines', copy=True, nauto_join=True)


    def init(self):
        tools.drop_view_if_exists(self._cr, 'flsp_comparebom_view')
        query = """
        CREATE or REPLACE VIEW flsp_comparebom_view AS (
        SELECT
            1 as id,
            mb1.id as bom1, mb1.code as code1, mb1.product_tmpl_id as product_templ_id1,
            mb1.product_qty as product_qty1, mb1.product_uom_id as product_uom_id1, mb1.version as version1, mb1.active as active1,
            mb2.id as bom2, mb2.code as code2, mb2.product_tmpl_id as product_tmpl_id2,
            mb2.product_qty as product_qty2, mb2.product_uom_id as product_uom_id2, mb2.version as version2, mb2.active as active2,
            'Compare BOMS' as page_name
        FROM mrp_bom as mb1
            inner join mrp_bom as mb2
            on 			mb2.id = (select bom2 from flsp_comparebom order by id desc limit 1)
            where 		mb1.id = (select bom1 from flsp_comparebom order by id desc limit 1)
        );
        """
        self.env.cr.execute(query)

    class FlspCompareBom(models.Model):
        """
            Purpose to hold the bom values to compare
        """
        _name = 'flsp.comparebom'
        _description = "FLSP BOM To Compare"

        bom1 = fields.Many2one('mrp.bom', string='BoM 1', required=True, ondelete='cascade')
        bom2 = fields.Many2one('mrp.bom', string='BoM 2', required=True, ondelete='cascade')
        sub_levels = fields.Boolean(string='Sublevels', default=False)

class FlspSalesForecast(models.Model):
    """
        Purpose: To get the bom line information to be used in a one to one field
    """
    _name = 'flsp.comparebom.line'
    _description = "FLSP BOM Line"
    _auto = False

    order_id = fields.Many2one('flsp.comparebom.view', string='Reference', required=True, ondelete='cascade', index=True, copy=False)
    # BoM line information
    id1 = fields.Float(string='BOMid1', readonly=True)
    id2 = fields.Float(string='BOMid2', readonly=True)
    product_line_id1 = fields.Many2one('product.product', string='BOM 1 Product', readonly=True)
    product_line_id2 = fields.Many2one('product.product', string='BOM 2 Product', readonly=True)
    product_line_qty1 = fields.Float(string='BOM 1 qty', readonly=True)
    product_line_qty2 = fields.Float(string='BOM 2 qty', readonly=True)
    bom_line_id1 = fields.Many2one('mrp.bom', string='Parent Bom_id 1')
    bom_comp_id1 = fields.Many2one('mrp.bom', string='Component bom_id 1')
    bom_level1 = fields.Integer(string='Bom level 1')
    bom_line_id2 = fields.Many2one('mrp.bom', string='Parent Bom_id 2')
    bom_comp_id2 = fields.Many2one('mrp.bom', string='Component bom_id 2')
    bom_level2 = fields.Integer(string='Bom level 2')

    uom_id1 = fields.Many2one('uom.uom', 'BOM 1 UoM', readonly=True)
    uom_id2 = fields.Many2one('uom.uom', 'BOM 2 UoM', readonly=True)

    def init(self):
        query = """

CREATE OR REPLACE FUNCTION flsp_bom_compare_function (query_type boolean)
RETURNS TABLE (id bigint, order_id int,
                id1 int, product_line_id1 int, product_line_qty1 numeric, bom_line_id1 int, bom_comp_id1 int, bom_level1 int, uom_id1 int,
                id2 int, product_line_id2 int, product_line_qty2 numeric, bom_line_id2 int, bom_comp_id2 int, bom_level2 int, uom_id2 int) LANGUAGE plpgsql as $$

BEGIN
    IF not query_type THEN
        RETURN QUERY
            -- FIRST LEVEL ONLY
            SELECT row_number() OVER() AS id, 1 as order_id,
                mbl1.bom_id as id1, mbl1.product_id as product_line_id1, mbl1.product_qty as product_line_qty1, 0 as bom_line_id1, 0 as bom_comp_id1, 1 as bom_level1, mbl1.product_uom_id as uom_id1,
                mbl2.bom_id as id2, mbl2.product_id as product_line_id2, mbl2.product_qty as product_line_qty2, 0 as bom_line_id2, 0 as bom_comp_id2, 1 as bom_level2, mbl2.product_uom_id as uom_id2
            FROM            (select * from mrp_bom_line where bom_id=(select bom1 from flsp_comparebom order by flsp_comparebom.id desc limit 1)) as mbl1
                full join 	(select * from mrp_bom_line where bom_id=(select bom2 from flsp_comparebom order by flsp_comparebom.id desc limit 1)) as mbl2
                on			mbl1.product_id = mbl2.product_id;

    ELSE
        RETURN QUERY
            -- ALL SUB LEVELS

            select row_number() OVER() AS id, 1 as order_id,
			    A.id1, A.product_line_id1, A.product_line_qty1, A.bom_line_id1, A.bom_comp_id1, A.bom_level1, A.uom_id1,
                B.id2, B.product_line_id2, B.product_line_qty2, B.bom_line_id2, B.bom_comp_id2, B.bom_level2, B.uom_id2
            from (
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
                                                            select lin, B1.id, sequence, product_tmpl_id from (
                                                            select row_number() OVER(PARTITION BY product_tmpl_id order by sequence) AS lin, mbsub1.id, sequence, product_tmpl_id  from mrp_bom as mbsub1 where active = true  order by product_tmpl_id
                                                            ) B1 where lin = 1

                                            ) as mb
                                            on 			pt.id = mb.product_tmpl_id) as table1
                            where mbl_bom_id = (select bom1 from flsp_comparebom order by flsp_comparebom.id desc limit 1)

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
                                                    select lin, B2.id, sequence, product_tmpl_id from (
                                                    select row_number() OVER(PARTITION BY product_tmpl_id order by sequence) AS lin, mbsub2.id, sequence, product_tmpl_id  from mrp_bom as mbsub2 where active = true  order by product_tmpl_id
                                                    ) B2 where lin = 1

                                    ) as mb
                                    on 			pt.id = mb.product_tmpl_id) as r
                            inner join	explode_bom1 eb on eb.bom_id = r.mbl_bom_id
                    )

                    --this is where we use the recursive table in the database
                    select    row_number() OVER(PARTITION BY product_id order by product_id, product_qty) AS prod_id1,
                                (select bom1 from flsp_comparebom order by flsp_comparebom.id desc limit 1) as id1 ,
                                product_id as product_line_id1, product_qty as product_line_qty1,
                                mbl_bom_id as bom_line_id1,
                                bom_id as bom_comp_id1,
                                level as bom_level1,
                                product_uom_id as uom_id1
                            from explode_bom1
            ) A
            full join (
            with recursive explode_bom2 as(
                        select 	        product_id, product_qty, mbl_bom_id, name, bom_id, 1 as level, product_uom_id
                            from 		(select 		mbl.product_id, mbl.product_qty, mbl.bom_id as mbl_bom_id, --pp.default_code,
                                                        pt.id, pt.name ,mb.id as bom_id, mbl.product_uom_id
                                            from		mrp_bom_line mbl
                                            inner join 	product_product as pp
                                            on			mbl.product_id = pp.id
                                            inner join 	product_template as pt
                                            on 			pp.product_tmpl_id = pt.id
                                            left join	(
                                                            select lin, B3.id, sequence, product_tmpl_id from (
                                                            select row_number() OVER(PARTITION BY product_tmpl_id order by sequence) AS lin, mbsub3.id, sequence, product_tmpl_id  from mrp_bom as mbsub3 where active = true  order by product_tmpl_id
                                                            ) B3 where lin = 1

                                            ) as mb
                                            on 			pt.id = mb.product_tmpl_id) as table1
                            where mbl_bom_id = (select bom2 from flsp_comparebom order by flsp_comparebom.id desc limit 1)

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
                                                    select lin, B4.id, sequence, product_tmpl_id from (
                                                    select row_number() OVER(PARTITION BY product_tmpl_id order by sequence) AS lin, mbsub4.id, sequence, product_tmpl_id  from mrp_bom AS mbsub4 where active = true  order by product_tmpl_id
                                                    ) B4 where lin = 1

                                    ) as mb
                                    on 			pt.id = mb.product_tmpl_id) as r
                            inner join	explode_bom2 eb on eb.bom_id = r.mbl_bom_id
                    )

                    --this is where we use the recursive table in the database
                    select    row_number() OVER(PARTITION BY product_id order by product_id, product_qty) AS prod_id2,
                                (select bom2 from flsp_comparebom order by flsp_comparebom.id desc limit 1) as id2 ,
                                product_id as product_line_id2, product_qty as product_line_qty2,
                                mbl_bom_id as bom_line_id2,
                                bom_id as bom_comp_id2,
                                level as bom_level2,
                                product_uom_id as uom_id2
                            from explode_bom2

            ) B
            on A.product_line_id1 = B.product_line_id2
            and A.prod_id1 = B.prod_id2;

    END IF;
END;
$$;


        CREATE or REPLACE VIEW flsp_comparebom_line AS (
            SELECT * FROM flsp_bom_compare_function((select sub_levels from flsp_comparebom order by id desc limit 1))
        );
        """
        self.env.cr.execute(query)
