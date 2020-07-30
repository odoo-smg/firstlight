# -*- coding: utf-8 -*-
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class SalesOrder(models.Model):
    _inherit = "sale.order"
    _check_company_auto = True

    @api.model
    def _default_sppepp(self):
        return self.env['ir.config_parameter'].sudo().get_param('flsp_sppepp')

    flsp_approval_required  = fields.Boolean(string="Approval Required", readonly=True, compute='_calc_sale_approval')
    flsp_approval_requested = fields.Boolean(string="Approval Requested", readonly=True)
    flsp_approval_approved  = fields.Boolean(string="Discount Approved", readonly=True)
    flsp_show_discount      = fields.Boolean(string="Show Disc. on Quote")
    flsp_order_line_count   = fields.Integer(string="Number of lines")
    flsp_ship_via           = fields.Char(string="Ship Via")
    flsp_so_attachment_ids = fields.Many2many('ir.attachment', 'flsp_so_attachment_rel', 'po_id', 'so_attachment_id',
        string='Sales Attachments',
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.')
    flsp_amount_deposit     = fields.Monetary(string='Deposit Payment', store=True, copy=False, readonly=True)
    flsp_products_pricelist = fields.One2many('product.product', 'id', 'Pricelist Products', compute='_calc_price_list_products')
    flsp_SPPEPP             = fields.Boolean(string="SPPEPP Active", default=_default_sppepp)
    flsp_SPPEPP_so          = fields.Boolean(string="School PPE Purchase Program", store=True)
    flsp_SPPEPP_leadtime    = fields.Selection([   ('4w', '4 Weeks'),
                                                ('10w', '10 Weeks'),
                                                ], string='Lead time', store=True, copy=False, default='10w')
    flsp_state = fields.Selection([
        ('draft', 'Quotation'),
        ('wait', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    sale_order_template_id = fields.Many2one(
        'sale.order.template', 'Quotation Template',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    sale_order_option_ids = fields.One2many(
        'sale.order.option', 'order_id', 'Optional Products Lines',
        copy=True, readonly=True,
        states={'draft': [('readonly', False)]})
    validity_date = fields.Date(string="Expiration", default = date.today() + relativedelta(days=30))



    @api.onchange('flsp_SPPEPP_so')
    def flsp_SPPEPP_so_onchange(self):
        pricelist_id = False
        if self.flsp_SPPEPP_so:
            pricelist_settings = self.env.company.flspsppepp_pricelist4w_id
            pricelist_settings10w = self.env.company.flspsppepp_pricelist10w_id
            if self.flsp_SPPEPP_leadtime == '4w':
                if pricelist_settings:
                    pricelist_id = pricelist_settings
                else:
                    sppepp_price_list_ids = self.env['product.pricelist'].search([
                        '&','&', '&',
                        ('flsp_SPPEPP_pl',  '=', True),
                        ('flsp_SPPEPP_leadtime', '=', self.flsp_SPPEPP_leadtime),
                        ('flsp_sale_type', '=', self.partner_id.flsp_sale_type),
                        ('currency_id', '=', self.partner_id.flsp_sale_currency.id)])
                    if sppepp_price_list_ids:
                        for sppepp_pricelist in sppepp_price_list_ids:
                            pricelist_id = sppepp_pricelist
            else:
                if pricelist_settings10w:
                    pricelist_id = pricelist_settings10w
                else:
                    sppepp_price_list_ids = self.env['product.pricelist'].search([
                        '&','&', '&',
                        ('flsp_SPPEPP_pl',  '=', True),
                        ('flsp_SPPEPP_leadtime', '=', self.flsp_SPPEPP_leadtime),
                        ('flsp_sale_type', '=', self.partner_id.flsp_sale_type),
                        ('currency_id', '=', self.partner_id.flsp_sale_currency.id)])
                    if sppepp_price_list_ids:
                        for sppepp_pricelist in sppepp_price_list_ids:
                            pricelist_id = sppepp_pricelist
        else:
            pricelist_id = self.partner_id.property_product_pricelist.id

        if pricelist_id:
            self.pricelist_id = pricelist_id

        return {
            'value': {
                'pricelist_id': pricelist_id
            },
        }

    @api.onchange('flsp_SPPEPP_leadtime')
    def flsp_SPPEPP_leadtime_onchange(self):
        pricelist_id = False
        if self.flsp_SPPEPP_so:
            pricelist_settings = self.env.company.flspsppepp_pricelist4w_id
            pricelist_settings10w = self.env.company.flspsppepp_pricelist10w_id
            if self.flsp_SPPEPP_leadtime == '4w':
                if pricelist_settings:
                    pricelist_id = pricelist_settings
                else:
                    sppepp_price_list_ids = self.env['product.pricelist'].search([
                        '&', '&', '&',
                        ('flsp_SPPEPP_pl', '=', True),
                        ('flsp_SPPEPP_leadtime', '=', self.flsp_SPPEPP_leadtime),
                        ('flsp_sale_type', '=', self.partner_id.flsp_sale_type),
                        ('currency_id', '=', self.partner_id.flsp_sale_currency.id)])
                    if sppepp_price_list_ids:
                        for sppepp_pricelist in sppepp_price_list_ids:
                            pricelist_id = sppepp_pricelist
            else:
                if pricelist_settings10w:
                    pricelist_id = pricelist_settings10w
                else:
                    sppepp_price_list_ids = self.env['product.pricelist'].search([
                        '&', '&', '&',
                        ('flsp_SPPEPP_pl', '=', True),
                        ('flsp_SPPEPP_leadtime', '=', self.flsp_SPPEPP_leadtime),
                        ('flsp_sale_type', '=', self.partner_id.flsp_sale_type),
                        ('currency_id', '=', self.partner_id.flsp_sale_currency.id)])
                    if sppepp_price_list_ids:
                        for sppepp_pricelist in sppepp_price_list_ids:
                            pricelist_id = sppepp_pricelist
        else:
            pricelist_id = self.partner_id.property_product_pricelist.id

        if pricelist_id:
            self.pricelist_id = pricelist_id

        return {
            'value': {
                'pricelist_id': pricelist_id,
            },
        }

    # To filter the domain of products based on price list
    @api.depends('pricelist_id')
    def _calc_price_list_products(self):
        product_ids = []
        price_list_line = self.env['product.pricelist.item'].search([('pricelist_id', '=', self.pricelist_id.id)])
        if price_list_line:
            price_list_lines_product_id = self.env['product.pricelist.item'].search([('pricelist_id', '=', self.pricelist_id.id)]).mapped("product_tmpl_id").ids
            if price_list_lines_product_id:
                product_ids = self.env['product.product'].search([('product_tmpl_id', 'in', price_list_lines_product_id)]).ids
        else:
            self.flsp_products_pricelist = False
            return
        for price_line in price_list_line:
            if price_line.base == 'pricelist':
                if price_line.applied_on == '3_global':
                    base_lines_product_id = self.env['product.pricelist.item'].search([('pricelist_id', '=', price_line.base_pricelist_id.id)]).mapped("product_tmpl_id").ids
                    product_line_ids = self.env['product.product'].search(['&',('product_tmpl_id', 'in', base_lines_product_id),('id','not in', product_ids)]).ids
                    product_ids = product_ids + product_line_ids
                if price_line.applied_on == '2_product_category':
                    base_lines_product_id = self.env['product.pricelist.item'].search([('pricelist_id', '=', price_line.base_pricelist_id.id)]).mapped("product_tmpl_id").ids
                    product_line_ids = self.env['product.product'].search(['&', '&', ('product_tmpl_id', 'in', base_lines_product_id), ('categ_id', '=', price_line.categ_id.id), ('id','not in', product_ids)]).ids
                    product_ids = product_ids + product_line_ids
        if product_ids:
            self.flsp_products_pricelist = product_ids

    @api.depends('order_line.discount')
    def _calc_sale_approval(self):
        self.flsp_approval_required = False
        flsp_sales_discount_approval = self.env['ir.config_parameter'].sudo().get_param('flsp_sales_discount_approval')
        so_flsp_max_percent_approval = self.env.company.so_flsp_max_percent_approval
        total_discount = 0.0
        self.flsp_order_line_count = 0
        for line in self.order_line:
            self.flsp_order_line_count = self.flsp_order_line_count +1
            if (line.discount > so_flsp_max_percent_approval) and flsp_sales_discount_approval:
                self.flsp_approval_required = True
            total_discount += line.discount

    def button_flsp_submit_approval(self):
        self.write({'flsp_approval_requested': True})
        return self.write({'flsp_state': 'wait'})

    def button_flsp_approve(self):
        #flsp_sale_order_lines = flspsaleapproval.Saleflspwizard
        #flsp_open_sale_wizard

        action = self.env.ref('flspsaleapproval.launch_flsp_sale_wizard').read()[0]
        return action

        #return self.action_confirm()

    def button_flsp_confirm(self):
        if not self.partner_id.flsp_acc_valid:
            action = self.env.ref('flspsaleapproval.launch_flsp_sale_message').read()[0]
        else:
            ## Validate deposit payment for School PPE Purchase Program
            flsp_sppepp = self.env['ir.config_parameter'].sudo().get_param('flsp_sppepp')
            flspsppepp_category_id = self.env.company.flspsppepp_category_id
            flsp_percent_sppepp = self.env.company.flsp_percent_sppepp
            if flsp_sppepp:
                amount_categ_total = 0
                for line in self.order_line:
                    if line.product_id.categ_id == flspsppepp_category_id:
                        amount_categ_total += line.price_subtotal
                if self.flsp_amount_deposit < (amount_categ_total*flsp_percent_sppepp/100):
                    action = self.env.ref('flspsaleapproval.launch_flsp_sppepp_message').read()[0]
                else:
                    action = self.action_confirm()
            else:
                action = self.action_confirm()

        return action

    def button_flsp_reject(self):
        self.write({'flsp_state': 'draft'})
        self.write({'flsp_approval_approved': False})
        self.write({'flsp_approval_requested': False})
        return self.write({'flsp_approval_requested': False})

    def sppepp_confirm(self):
        action = self.action_confirm()
        return action


    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['flsp_state'] = 'draft'
        default['flsp_approval_requested'] = False
        default['flsp_approval_approved'] = False
        default['flsp_approval_required'] = False
        return super(SalesOrder, self).copy(default=default)