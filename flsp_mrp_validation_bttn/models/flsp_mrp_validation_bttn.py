# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class product_template(models.Model):
    """
        class_name: product_template
        model_name: product.template
        Purpose:    To add flsp mrp validation bttn to the product
        Date:       March.10th.2021.W
        Author:     Sami Byaruhanga
    """
    _inherit = 'product.template'

    flsp_mrp_bttn = fields.Boolean(string='MRP Validated', default=False, store=True, copy=False)

    def button_mrp_valid(self):
        """
            Purpose:    To validated product template
        """
        self.write({'flsp_mrp_bttn': True})

    def button_mrp_unvalid(self):
        """
            Purpose:    To unvalidate product template
        """
        self.write({'flsp_mrp_bttn': False})


class mrp_production(models.Model):
    """
        class_name: mrp_production
        model_name: mrp.production
        Purpose:    To return a validation error when product is not mrp validated
        Date:       March.10th.2021.W
        Author:     Sami Byaruhanga
    """
    _inherit = 'mrp.production'

    check_mrp_valid = fields.Boolean(string='mrp valid', default=False, store=True, copy=False)

    def database_return_table(self):
        """
            Purpose:    To check that all product are mrp_validated and returns a table
            Returns:    List of all the products id, and name from database
        """
        self._cr.execute("""
                    with recursive explode_bom as(
                        select 			pdct_temp_id, flsp_mrp_bttn, mbl_bom_id, name, bom_id, 1 as level
                            from 		(select 		pt.id as pdct_temp_id, pt.flsp_mrp_bttn, mbl.bom_id as mbl_bom_id,
                                            pt.name ,mb.id as bom_id
                                            from		mrp_bom_line mbl
                                            inner join 	product_product as pp
                                            on			mbl.product_id = pp.id
                                            inner join 	product_template as pt
                                            on 			pp.product_tmpl_id = pt.id
                                            full join	mrp_bom as mb
                                            on 			pt.id = mb.product_tmpl_id
                                        ) as table1
                            where 		mbl_bom_id= %s

                        union -- recursive part now
                            select 		r.pdct_temp_id,
                                        r.flsp_mrp_bttn, r.mbl_bom_id, r.name, r.bom_id, eb.level + 1 AS level
                            from 		(select 		pt.id as pdct_temp_id, pt.flsp_mrp_bttn, mbl.bom_id as mbl_bom_id,
                                            pt.name ,mb.id as bom_id
                                            from		mrp_bom_line mbl
                                            inner join 	product_product as pp
                                            on			mbl.product_id = pp.id
                                            inner join 	product_template as pt
                                            on 			pp.product_tmpl_id = pt.id
                                            full join	mrp_bom as mb
                                            on 			pt.id = mb.product_tmpl_id
                                        ) as r
                            inner join	explode_bom eb on eb.bom_id = r.mbl_bom_id
                    )
                    --select      eb.pdct_temp_id, eb.flsp_mrp_bttn	from explode_bom as eb
                    --select      eb.pdct_temp_id	from explode_bom as eb
                    select      pt.default_code, pt.name
                    from        explode_bom as eb
                    inner join  product_template as pt
                    on          eb.pdct_temp_id = pt.id
                    inner join  product_product as pp
                    on          pt.id = pp.product_tmpl_id

                    where       eb.flsp_mrp_bttn is null or eb.flsp_mrp_bttn = 'False';
                    """ % (self.bom_id.id,)  # %we are passing the current id bom_id to explode
                         )
        table = self._cr.fetchall()
        return table

    @api.onchange('bom_id', 'date_planned_state')
    def set_check_mrp_valid_field(self):
        """
            Purpose: on changing the bom, we call database return to check if products are mrp validated
                     if all validated the check_mrp_valid set to false else true
        """
        if self.bom_id:
            table = self.database_return_table()
            if len(table) > 0:
                self.write({'check_mrp_valid': True})
            else:
                self.write({'check_mrp_valid': False})

    def clean_table(self, table):
        """
            Purpose:    To clean the table so we are able to raise a meaningful error to the user
            Return:     Returns the list of products that need to be mrp validated.
        """
        # print("Cleaning the table*************************************")
        test = []
        for line in table:
            for line2 in line:
                test.append(line2)
        i = 0
        new_table = ["The following products are not MRP Validated."
                     " To continue production Please Validate these products"]
        while i < (len(test) + 1):
            new_table.append("\n" + ("[" + test[i] + "] - " + test[i + 1]) )
            i += 2
            if (i - 1) == len(test) - 1:
                break
        return new_table

    def button_mrp_validation_check(self):
        """
            Purpose:    To check if the products are mrp validated and plm validated
            Returns:    The action confirm
            Note:       This button overrides the previous bttn actions in the xml code
        """
        if len(self.database_return_table()) == 0:
            self.write({'check_mrp_valid': False})
            # print(self.check_mrp_valid)
        if self.check_mrp_valid:
            # print(self.check_mrp_valid)
            # print("RAISING THE VALIDATION ERROR")
            raise ValidationError((self.clean_table(self.database_return_table())))
        elif not self.bom_id.flsp_bom_plm_valid:
            # print("PLM validation error")
            action = self.env.ref('flsp-mrp.launch_flsp_wizprd_message').read()[0]
        elif not self.check_mrp_valid and self.bom_id.flsp_bom_plm_valid:
            # print("No errors where raised in the validation process")
            action = self.action_confirm()
        return action

class product_product(models.Model):
    """
        class_name: product_product
        model_name: product.product
        Purpose:    To add flsp mrp validation bttn to the product
        Date:       March.12th.2021.F
        Author:     Sami Byaruhanga
    """
    _inherit = 'product.product'
    flsp_mrp_bttn = fields.Boolean(string='MRP Validated', default=False, store=True, copy=False)
    def button_mrp_valid(self):
        """
            Purpose:    To validated product template
        """
        self.product_tmpl_id.flsp_mrp_bttn = True
        return self.write({'flsp_mrp_bttn': True})
        # self.write({'flsp_mrp_bttn': True})
    def button_mrp_unvalid(self):
        """
            Purpose:    To unvalidate product template
        """
        self.product_tmpl_id.flsp_mrp_bttn = False
        return self.write({'flsp_mrp_bttn': False})
        
