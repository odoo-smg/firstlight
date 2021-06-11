# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import timedelta
import dateutil.rrule as rrule
from datetime import datetime


class flspsalesorderline(models.Model):
    _inherit = 'sale.order.line'

    flsp_partner_id = fields.Many2one('res.partner', 'Customer Name', store=True, readonly=True, related="order_id.partner_id")
    flsp_ship_date = fields.Datetime('Shipping Date', store=True)
    flsp_date_order = fields.Datetime('Order Date', store=True, readonly=True, related="order_id.date_order")
    is_today = fields.Boolean('Today', compute='_compute_shipping_date')
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

    @api.depends('order_partner_id')
    def _compute_shipping_date(self):
        current_date = datetime.now()
        current_date_str = str(current_date)[0:10]
        date_week = current_date + timedelta(days=6-current_date.weekday())
        date_week_str = str(date_week)[0:10]
        for move in self:
            move.flsp_ship_date = move.order_id.commitment_date
            for line in move.order_id.order_line:
                line.flsp_ship_date = move.order_id.commitment_date
            move.is_today = False
            #move.is_week = False
            if str(move.flsp_ship_date)[0:10] == current_date_str:
                move.is_today = True
            #elif str(move.date_expected)[0:10] <= date_week_str:
                #move.is_week = True
