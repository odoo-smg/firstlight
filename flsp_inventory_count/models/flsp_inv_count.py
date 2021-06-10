# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from datetime import datetime

class FlspMrpPlanningLine(models.Model):
    _name = 'flsp.inv.count'
    _description = 'FLSP Weekly Transfer'

    name = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product template', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    flsp_inv_date = fields.Date('Last Count')
    flsp_inv_user_id = fields.Many2one('res.users', 'Counting Responsible')
    tracking = fields.Selection(related="product_id.tracking")
    location_id = fields.Many2one('stock.location', string='Location', related="product_id.location_id")
    flsp_inv_count = fields.Boolean('To count', default=True)
    flsp_counted = fields.Boolean('Counting', default=False)

    def _replicate_resp(self):
        resp = ''
        for line in self:
            if line.flsp_inv_user_id:
                resp = line.flsp_inv_user_id

        for line in self:
            line.flsp_inv_user_id = resp

    def mark_done(self):
        if self.flsp_counted:
            product_prd = self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)], limit=1)
            if product_prd:
                product_prd.product_tmpl_id.flsp_inv_date = datetime.today()
                product_prd.product_tmpl_id.flsp_inv_user_id = self.env.user
                product_prd.product_tmpl_id.flsp_inv_count = False
                self.flsp_inv_count = False
                if not self.flsp_inv_user_id:
                    self.flsp_inv_user_id = self.env.user

    def confirm(self):
        #print('checking this product')
        #self.product_tmpl_id.action_open_quants()
        self.flsp_counted = True
        product_product = self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)], limit=1)
        domain = [('product_id', 'in', product_product.ids)]
        hide_location = not self.user_has_groups('stock.group_stock_multi_locations')
        hide_lot = all([product.tracking == 'none' for product in product_product])
        self = self.with_context(hide_location=hide_location, hide_lot=hide_lot)

        # If user have rights to write on quant, we define the view as editable.
        #if self.user_has_groups('stock.group_stock_manager'):
        self = self.with_context(inventory_mode=True)
        # Set default location id if multilocations is inactive
        #if not self.user_has_groups('stock.group_stock_multi_locations'):
        user_company = self.env.company
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', user_company.id)], limit=1
        )
        if warehouse:
            self = self.with_context(default_location_id=warehouse.lot_stock_id.id)
        # Set default product id if quants concern only one product
        if len(self) == 1:
            self = self.with_context(
                default_product_id=product_product.id,
                single_product=True
            )
        else:
            self = self.with_context(product_tmpl_ids=self.product_product.ids)
        ctx = dict(self.env.context)
        ctx.update({'no_at_date': True, 'search_default_internal_loc': True})
        return self.env['stock.quant'].with_context(ctx)._get_quants_action(domain)
