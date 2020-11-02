# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api
from datetime import datetime


class SummarizedBomReport(models.Model):
    _name = 'report.flsp.summarized.bom'
    _auto = False
    _description = 'Summarized BOM Report'

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    bom_id = fields.Many2one(comodel_name="mrp.bom", string="BOM")
    product_qty = fields.Float(string='Qty required', readonly=True)
    level_bom = fields.Integer(String="BOM Level", readonly=True, help="Position of the product inside of a BOM.")

    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_flsp_summarized_bom')


        query = """

        create table IF NOT EXISTS TMP_TABLE_CALCULATION (id Integer, description text, default_code text, product_tmpl_id Integer, product_id Integer, bom_id Integer, product_qty double precision, level_bom integer);
        TRUNCATE TMP_TABLE_CALCULATION;
        """
        self.env.cr.execute(query)

        query = """

        CREATE OR REPLACE PROCEDURE flsp_include_products_on_tmp(bom_id_par integer, bom_level integer, bom_factor float)
        AS $$

		declare
             next_id    integer;
			 product_bom_qty integer;
			 product_bom_id  integer;
             current_bom_line   record;
             current_bom_cursor refcursor;
        begin

			--raise notice '   %starting flsp_include_products_on_tmp for bom_id_par= %  and level=%' , concat(repeat('      ',bom_level),'|---'), bom_id_par, bom_level;

			if(bom_id_par is not NULL) then
			   --raise notice '      %openning cursor of mrp_bom_lines...', concat(repeat('      ',bom_level),'|---') ;
	           open current_bom_cursor for select * from mrp_bom_line where bom_id = bom_id_par;
			end if ;

           loop

   			  --raise notice '         %getting next...', concat(repeat('      ',bom_level),'|---   ');

              fetch current_bom_cursor into current_bom_line;
              exit when not found;

   			  --raise notice '         %inserting for product=...%', concat(repeat('      ',bom_level),'|---   '), current_bom_line.product_id;
			  product_bom_qty := (select count(id) as TOTAL from mrp_bom where product_tmpl_id in (select product_tmpl_id from product_product where id = current_bom_line.product_id));
			  product_bom_id := (select id from mrp_bom where product_tmpl_id in (select product_tmpl_id from product_product where id = current_bom_line.product_id) limit 1);
   			  --raise notice '         %boms for the product = %', concat(repeat('      ',bom_level),'|---   '), product_bom_qty;
			  if product_bom_qty > 0 then
	  	  		--raise notice '         %re-calling the function on this product for bom_id = %', concat(repeat('      ',bom_level),'|---   '), product_bom_id;
	            bom_level := bom_level + 1;
			  	call flsp_include_products_on_tmp(product_bom_id, bom_level, current_bom_line.product_qty*bom_factor);
			  else
				  next_id := (select count(id) as TOTAL from TMP_TABLE_CALCULATION);
				  next_id := next_id + 1;
				  INSERT INTO TMP_TABLE_CALCULATION
					select     next_id as id,
							   product_template.name as description,
							   product_template.default_code,
							   product_template.id as product_tmpl_id,
							   current_bom_line.product_id,
							   bom_id_par,
							   current_bom_line.product_qty*bom_factor,
							   bom_level as level_bom
					from       product_product
					inner join product_template
					on         product_template.id = product_product.product_tmpl_id
					where      product_product.id = current_bom_line.product_id;
			  end if;
           end loop;

           close current_bom_cursor;

        end;
        $$
        language plpgsql;
        """

        self.env.cr.execute(query)

        query = """

        CREATE OR REPLACE PROCEDURE flsp_load_boms()
        AS $$

        declare
             bom_line   record;
             bom_cursor cursor
                 for select * from flsp_bom_summarized;
        begin

           raise notice 'starting procedure: flsp_load_boms!';

        -- open the cursor
           open bom_cursor;
           --raise notice '   opening cursor!';
           loop
            -- fetch row into the film
              fetch bom_cursor into bom_line;
            -- exit when no more row to fetch
              exit when not found;
              --raise notice '   checking bom_id = %',  bom_line.bom_id;
              if bom_line.bom_id is not null then
			    --raise notice '   calling flsp_include_products_on_tmp for bom_id = %',  bom_line.bom_id;
                call flsp_include_products_on_tmp(bom_line.bom_id, 0, bom_line.product_qty);
              end if;
           end loop;

           -- close the cursor
           close bom_cursor;

        end;

        $$
        language plpgsql;

        """

        self.env.cr.execute(query)

        query = """

        CALL flsp_load_boms();

        """

        self.env.cr.execute(query)

        query = """

        CREATE or REPLACE VIEW report_flsp_summarized_bom AS (
        SELECT
            max(TMP_TABLE_CALCULATION.id) as id,
            product_template.name as description,
            product_template.default_code as default_code,
            product_product.product_tmpl_id as product_tmpl_id,
            TMP_TABLE_CALCULATION.product_id,
            max(TMP_TABLE_CALCULATION.bom_id) as bom_id,
            sum(TMP_TABLE_CALCULATION.product_qty) as product_qty,
            max(TMP_TABLE_CALCULATION.level_bom) as level_bom
        FROM TMP_TABLE_CALCULATION
		inner join product_product
		on         product_product.id = TMP_TABLE_CALCULATION.product_id
		inner join product_template
		on         product_template.id = product_product.product_tmpl_id
		group by TMP_TABLE_CALCULATION.product_id, product_product.product_tmpl_id, product_template.name, product_template.default_code        );
        """

        self.env.cr.execute(query)
