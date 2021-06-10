# -*- coding: utf-8 -*-

from odoo import fields, models, api


class flspsalesorderline(models.Model):
    _inherit = 'sale.order.line'

    flsp_partner_id = fields.Many2one('res.partner', 'Customer', store=True, readonly=True, related="order_id.partner_id")
    flsp_ship_date = fields.Datetime('Shipping Date', readonly=True, related="order_id.commitment_date")
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
        ('kk-cancel', 'Cancelled'), ], string='Status', readonly=True, related="order_id.flsp_bpm_status")
