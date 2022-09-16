# -*- coding: utf-8 -*-
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


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
        ], string='Discount Status', readonly=True, copy=False, index=True, default='draft')

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

    flsp_att_to = fields.Many2one("flsp.contact", string='Attention to', domain="[('partner_id', '=', partner_id)]")
    flsp_internal_notes = fields.Text('Internal Notes')
    flsp_delivery_contact = fields.Many2one("flsp.contact", string='Delivery Contact', domain="[('partner_id', '=', partner_shipping_id)]", help='The contact for the "Delivery Adress"')
    flsp_delivery_tax = fields.Char(string='Tax ID', help='The Tax ID for the "Delivery Adress"')
    
    @api.onchange('partner_shipping_id')
    def onchange_partner_shipping_id_for_delivery_contact(self):
        if self.partner_shipping_id and self.partner_shipping_id.flsp_contacts_ids:
            contacts = self.partner_shipping_id.flsp_contacts_ids
            primary_contact = contacts[0]
            for contact in contacts:
                if contact.sequence < primary_contact.sequence:
                    primary_contact = contact
            self.flsp_delivery_contact = primary_contact
        else:
            self.flsp_delivery_contact = False

    @api.onchange('flsp_delivery_contact')
    def onchange_flsp_delivery_contact(self):
        if self.partner_shipping_id and self.partner_shipping_id.flsp_contacts_ids:
            contacts = self.partner_shipping_id.flsp_contacts_ids
            # match the contact and reorganize the flsp_contacts_ids with flsp_delivery_contact as the first/primary one
            index = 0
            for contact in contacts:
                if contact.id == self.flsp_delivery_contact.id:
                    index = contact.sequence
                    break
            if index == 0:
                # it has been the first one
                return
            # set it as the first one and update others as well because a contact is ahead of the other if its sequence is smaller than the latter
            for contact in contacts:
                if contact.sequence < index:
                    contact.sequence += 1
                if contact.sequence == index and contact.id != self.flsp_delivery_contact.id:
                    contact.sequence += 1
            self.flsp_delivery_contact.sequence = 0

    @api.onchange('partner_id')
    def onchange_taxt_id(self):
        if self.partner_id and self.partner_id.vat:
            self.flsp_delivery_tax = self.partner_id.vat
        else:
            self.flsp_delivery_tax = False

    @api.onchange('flsp_delivery_tax')
    def onchange_flsp_delivery_tax(self):
        if self.partner_id:
            self.partner_id.vat = self.flsp_delivery_tax

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
        #self.request_approval_by_email()
        self.env['flspautoemails.bpmemails'].send_email(self, 'SO0001')
        self.write({'flsp_approval_requested': True})
        return self.write({'flsp_state': 'wait'})

    def request_approval_by_email(self):
        template = self.env.ref('flspautoemails.flsp_soapprovreq_tmpl', raise_if_not_found=False)

        if not template:
            _logger.warning('Template "flspautoemails.flsp_soapprovreq_tmpl" was not found. Cannot send the approval request for Sales Order.')
            return

        d_from = date.today()
        so_id = self.id
        rendered_body = template.render({'docids': self.env['sale.order'].search([('id', '=', so_id)]),
                                         'd_from': d_from}, engine='ir.qweb')
        body = self.env['mail.thread']._replace_local_links(rendered_body)
        body += '<br/><br/><br/>'
        body += '<div style = "text-align: center;" >'
        body += '  <a href = "https://odoo-smg-firstlight1.odoo.com/web#action=408&amp;model=sale.order&amp;view_type=list&amp;cids=1&amp;menu_id=230" style = "background: #1abc9c; padding: 20px; text-decoration: none; color: #fff; border-radius: 5px; font-size: 16px;" class ="o_default_snippet_text">Access Sales Order</a>'
        body += '  <br/><br/><br/>'
        body += '</div>'
        body += '<p>Thank you!</p>'

        self.env['mail.mail'].create({
            'body_html': body,
            'subject': 'Odoo - Sales Discount Approval Request',
            'email_to': 'camquan@smartrendmfg.com;stephanieaddy@smartrendmfg.com; alexandresousa@smartrendmfg.com; '+self.user_id.login,
            'auto_delete': True,
        }).send()

    def button_flsp_approve(self):
        #flsp_sale_order_lines = flspsaleapproval.Saleflspwizard
        #flsp_open_sale_wizard

        action = self.env.ref('flspsaleapproval.launch_flsp_sale_wizard').read()[0]
        return action

        #return self.action_confirm()
    def button_flsp_cancel(self):
        self.flsp_approval_requested = False
        self.flsp_approval_approved = False
        self.flsp_state = 'draft'
        action = self.env.ref('flspsaleapproval.launch_flsp_cancel_wizard').read()[0]
        return action

    def wiz_cancel_confirm(self):
        action = self.action_cancel()
        return action

    def button_flsp_confirm(self):
        # Validate customer's acc status
        if not self.partner_id.flsp_acc_valid:
            return self.env.ref('flspsaleapproval.launch_flsp_sale_message').read()[0]
        
        # # Validate Tax ID when to confirm Sales Order
        # if not self.partner_id.vat:
        #     ca_id = self.env['res.country'].search([('name', '=', 'Canada')])
        #     if self.partner_shipping_id.country_id != ca_id:
        #         return self.env.ref('flspsaleapproval.launch_flsp_sale_delivery_message').read()[0]
        
        # # Validate Contact Information when to confirm Sales Order
        # if not self.partner_shipping_id.flsp_contacts_ids or not self.flsp_delivery_contact:
        #     return self.env.ref('flspsaleapproval.launch_flsp_sale_delivery_message').read()[0]
        # primary_contact = self.partner_shipping_id.flsp_contacts_ids[0]
        # if not primary_contact.name:
        #     return self.env.ref('flspsaleapproval.launch_flsp_sale_delivery_message').read()[0]
        # if not primary_contact.phone:
        #     return self.env.ref('flspsaleapproval.launch_flsp_sale_delivery_message').read()[0]
        
        # Validate deposit payment for School PPE Purchase Program
        flsp_sppepp = self.env['ir.config_parameter'].sudo().get_param('flsp_sppepp')
        flspsppepp_category_id = self.env.company.flspsppepp_category_id
        flsp_percent_sppepp = self.env.company.flsp_percent_sppepp
        if flsp_sppepp:
            amount_categ_total = 0
            for line in self.order_line:
                if line.product_id.categ_id == flspsppepp_category_id:
                    amount_categ_total += line.price_subtotal
            if self.flsp_amount_deposit < (amount_categ_total*flsp_percent_sppepp/100):
                return self.env.ref('flspsaleapproval.launch_flsp_sppepp_message').read()[0]
                
        # all the prechecks pass
        # sends an email to FLorders@firstlightsafety.com
        self.env['flspautoemails.bpmemails'].send_email(self, 'SO0006')
        #self.flsp_email_order_confirmed()
        return self.action_confirm()

    def flsp_email_order_confirmed(self):
        template = self.env.ref('flspsaleapproval.flsp_confirmed_order_email', raise_if_not_found=False)

        if not template:
            _logger.warning('Template "flspsaleapproval.flsp_confirmed_order_email" was not found. Cannot send the confirmation for Sales Order.')
            return

        rendered_body = template.render({'docids': self,
                                         'sale_order_line': self.order_line}, engine='ir.qweb')
        body = self.env['mail.thread']._replace_local_links(rendered_body)

        self.env['mail.mail'].create({
            'body_html': body,
            'subject': 'Odoo - Sales Order Confirmed',
            'email_to': 'FLorders@firstlightsafety.com; alexandresousa@smartrendmfg.com; '+self.user_id.login,
            'auto_delete': True,
        }).send()

    def button_flsp_reject(self):
        action = self.env.ref('flspsaleapproval.launch_flsp_reject_wizard').read()[0]
        return action

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
