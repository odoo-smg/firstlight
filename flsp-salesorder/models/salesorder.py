# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class flspsalesorder(models.Model):
    _inherit = 'sale.order'

    flsp_so_user_id = fields.Many2one('res.users', string="Inside Salesperson")
    flsp_so_dss_user_id = fields.Many2one('res.users', string="Dealer Specialist")
    flsp_include_invoice = fields.Boolean('Include Invoice', default=True)
    flsp_amount_deposit = fields.Monetary(string='Deposit Payment', store=True, copy=False, readonly=True)
    flsp_bpm_status = fields.Selection([
        ('quote', 'Quote'),
        ('wait', 'Waiting Approval'),
        ('approved', 'Disc.Approved'),
        ('sale', 'Sales Order'),
        ('confirmed', 'Delivery Confirmed'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('partial', 'Partially Shipped'),
        ('tracking', 'Tracking Assigned'),
        ('delivered', 'Delivered'),
        ('cancel', 'Cancelled'),
        ('aa-quote', 'Quote'),
        ('bb-wait', 'Waiting Approval'),
        ('cc-approved', 'Disc.Approved'),
        ('dd-sale', 'Sales Order'),
        ('ee-confirmed', 'Shipping Confirmed'),
        ('ff-packed', 'Packed'),
        ('gg-partial', 'Partially Shipped'),
        ('hh-shipped', 'Shipped'),
        ('ii-tracking', 'Tracking Assigned'),
        ('jj-delivered', 'Delivered'),
        ('kk-cancel', 'Cancelled'),
        ], string='FL Status', copy=False, index=True, store=True, default='aa-quote')

    flsp_shipping_method = fields.Selection([
        ('1', 'FL account and Invoice the Customer'),
        ('2', 'FL account and do not Invoice Customer'),
        ('3', 'Customer carrier choice and account'),
        ], string='Shipping Method', copy=False, store=True)
    flsp_carrier_account = fields.Char(String="Carrier Account")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'payment_term_id': False,
                'fiscal_position_id': False,
                'flsp_so_user_id': False,
                'flsp_so_dss_user_id': False,
                'flsp_shipping_method': False,
                'flsp_ship_via': False,
                'flsp_carrier_account': False,
            })
            return

        addr = self.partner_id.address_get(['delivery', 'invoice'])
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        delivery_addresses = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id)])
        default_address = addr['delivery']
        default_invoice = addr['invoice']
        default_shipping_method = self.partner_id.flsp_shipping_method
        default_ship_via = self.partner_id.property_delivery_carrier_id.name
        default_shipping_account = self.partner_id.flsp_carrier_account
        for delivery in delivery_addresses:
            if delivery.flsp_default_contact and delivery.type == "delivery":
                default_address = delivery.id
                default_shipping_method = delivery.flsp_shipping_method
                default_ship_via = delivery.property_delivery_carrier_id.name
                default_shipping_account = delivery.flsp_carrier_account
            if delivery.flsp_default_contact and delivery.type == "invoice":
                default_invoice = delivery.id

        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': default_invoice,
            'partner_shipping_id': default_address,
            'flsp_so_user_id': self.partner_id.flsp_user_id.id or self.env.uid,
            'flsp_so_dss_user_id': self.partner_id.flsp_dss_user_id.id,
            'flsp_shipping_method': default_shipping_method,
            'flsp_ship_via': default_ship_via,
            'flsp_carrier_account': default_shipping_account,
            'user_id': partner_user.id
        }
        if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.env.company.invoice_terms:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms

        # Use team of salesman if any otherwise leave as-is
        values['team_id'] = partner_user.team_id.id if partner_user and partner_user.team_id else self.team_id
        self.update(values)

    @api.onchange('partner_shipping_id', 'partner_id')
    def flsp_onchange_partner_shipping_id(self):
        values = {
            'flsp_shipping_method': self.partner_shipping_id.flsp_shipping_method,
            'flsp_ship_via': self.partner_shipping_id.property_delivery_carrier_id.name,
            'flsp_carrier_account': self.partner_shipping_id.flsp_carrier_account,
        }

        self.update(values)
        return {}


class flspsalesorderline(models.Model):
    _inherit = 'sale.order.line'
    
    customerscode_ids = fields.Many2one('flspstock.customerscode', 'Customer Part Number')

    @api.onchange('product_id')
    def flsp_product_id_onchange(self):
        for rec in self:
            return {'domain': {'customerscode_ids': [('partner_id', '=', rec.order_id.partner_id)]}}
    
    @api.onchange('product_uom_qty')
    def flsp_product_uom_qty_onchange(self):
        ret_val = {}
        value_ret = self.product_uom_qty
        if self.product_uom_qty < self.product_template_id.flsp_min_qty:
            value_ret = self.product_template_id.flsp_min_qty
            self.product_uom_qty = value_ret
            ret_val = {'value': {'product_uom_qty': value_ret}}
        return ret_val

    @api.onchange('product_template_id')
    def flsp_product_template_id_onchange(self):
        ret_val = {}
        value_ret = self.product_uom_qty
        if self.product_uom_qty < self.product_template_id.flsp_min_qty:
            value_ret = self.product_template_id.flsp_min_qty
            self.product_uom_qty = value_ret
            ret_val = {'value': {'product_uom_qty': value_ret}}
        return ret_val
