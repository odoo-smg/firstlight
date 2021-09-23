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

    # bom_line_ids1 = fields.One2many('mrp.bom.line', 'bom_id', 'BoM Lines', copy=True)
    code1 = fields.Char('Reference', readonly=True)
    # type1 = fields.Char('Type', readonly=True)
    # type = fields.Selection([('normal', 'Manufacture this product'), ('phantom', 'Kit')], 'BoM Type')
    product_tmpl_id1 = fields.Many2one('product.template', string='Product template', readonly=True)
    product_qty1 = fields.Float(string='Quantity', readonly=True)
    version1 = fields.Float(string='Version', readonly=True)
    active1 = fields.Boolean(string='Active')
    product_uom_id1 = fields.Many2one('uom.uom', 'Product UoM', readonly=True)

    # bom_line_ids2 = fields.One2many('mrp.bom.line', 'bom_id', 'BoM Lines', copy=True)
    code2 = fields.Char('Reference', readonly=True)
    # type2 = fields.Char('Type', readonly=True)
    product_tmpl_id2 = fields.Many2one('product.template', string='Product template', readonly=True)
    product_qty2 = fields.Float(string='Quantity', readonly=True)
    version2 = fields.Float(string='Version', readonly=True)
    active2 = fields.Boolean(string='Active')
    product_uom_id2 = fields.Many2one('uom.uom', 'Product UoM', readonly=True)

    # bom_line = fields.One2many('flsp.comparebom.line', 'order_id', string='Order Lines', copy=True, nauto_join=True)
    bom_line = fields.One2many('flsp.comparebom.line', 'order_id', string='Order Lines', copy=True, nauto_join=True)

    # # BoM line information
    # # forecast_line = fields.One2many('flsp.sales.forecast.line', 'order_id', string='Order Lines', copy=True, nauto_join=True)
    # # default_code = fields.Char(string='Part #', readonly=True)
    # id1 = fields.Float(string='id1', readonly=True)
    # id2 = fields.Float(string='id2', readonly=True)
    # product_line_id1 = fields.Many2one('product.product', string='Product', readonly=True)
    # product_line_id2 = fields.Many2one('product.product', string='Product', readonly=True)
    # product_line_qty1 = fields.Float(string='qty', readonly=True)
    # product_line_qty2 = fields.Float(string='qty', readonly=True)
    # uom_id1 = fields.Many2one('uom.uom', 'Product UoM', readonly=True)
    # uom_id2 = fields.Many2one('uom.uom', 'Product UoM', readonly=True)
    #
    # # product_tmpl_id_comp = fields.Many2one('product.template', string='Product template', readonly=True)
    # # product_id_comp = fields.Many2one('product.product', string='Product', readonly=True)
    # # #Compare both BoMs line
    # # in_bom1 = fields.Boolean(string="BoM 1", default=False, readonly=True)
    # # in_bom2 = fields.Boolean(string="BoM 2", default=False, readonly=True)

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

        # query = """
        # SELECT
        #     mbl1.bom_id as id1, mbl1.product_id as product_line_id1, mbl1.product_qty as product_line_qty1, mbl1.product_uom_id as uom_id1,
        #     mbl2.bom_id as id2, mbl2.product_id as product_line_id2, mbl2.product_qty as product_line_qty2, mbl2.product_uom_id as uom_id2
        # FROM            (select * from mrp_bom_line where bom_id=(select bom1 from flsp_comparebom order by id desc limit 1)) as mbl1
        #     full join 	(select * from mrp_bom_line where bom_id=(select bom2 from flsp_comparebom order by id desc limit 1)) as mbl2
        #     on			mbl1.product_id = mbl2.product_id
        # """
        # print("executing query #2")
        # self.env.cr.execute(query)


    class FlspCompareBom(models.Model):
        """
            Purpose to hold the bom values to compare
        """
        _name = 'flsp.comparebom'
        _description = "FLSP BOM To Compare"

        bom1 = fields.Many2one('mrp.bom', string='BoM 1', required=True, ondelete='cascade')
        bom2 = fields.Many2one('mrp.bom', string='BoM 2', required=True, ondelete='cascade')

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
    uom_id1 = fields.Many2one('uom.uom', 'BOM 1 UoM', readonly=True)
    uom_id2 = fields.Many2one('uom.uom', 'BOM 2 UoM', readonly=True)

    def init(self):
        query = """
        CREATE or REPLACE VIEW flsp_comparebom_line AS (
        SELECT
            --1 as id,
            row_number() OVER() AS id,
            1 as order_id ,
            mbl1.bom_id as id1, mbl1.product_id as product_line_id1, mbl1.product_qty as product_line_qty1, mbl1.product_uom_id as uom_id1,
            mbl2.bom_id as id2, mbl2.product_id as product_line_id2, mbl2.product_qty as product_line_qty2, mbl2.product_uom_id as uom_id2
        FROM            (select * from mrp_bom_line where bom_id=(select bom1 from flsp_comparebom order by id desc limit 1)) as mbl1
            full join 	(select * from mrp_bom_line where bom_id=(select bom2 from flsp_comparebom order by id desc limit 1)) as mbl2
            on			mbl1.product_id = mbl2.product_id
        );
        """
        # print("executing query #2")
        self.env.cr.execute(query)
