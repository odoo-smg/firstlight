# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class flspaccountmove(models.Model):
    _inherit = 'account.move'
    _check_company_auto = True

    flsp_broker_id = fields.Many2one('res.partner', string='Broker')
    flsp_ci_notes = fields.Text(string='Notes for Commercial Invoice')
    
    @api.depends('invoice_origin')
    def _get_so(self):
        self.flsp_sale_orders = self.env['sale.order'].search([('name', '=', self.invoice_origin.strip())])
        self.flsp_delivery_id = self._get_default_delivery()
    
    def _get_default_delivery(self):
        if self.flsp_delivery_id:
            return self.flsp_delivery_id
        
        # initialize flsp_delivery_id
        latest_delivery = False
        now_date = datetime.now()
        deliveries = self.env['stock.picking'].search([('sale_id', 'in', self.flsp_sale_orders.ids)], order="scheduled_date")
        for d in deliveries:
            if not latest_delivery:
                latest_delivery = d
            else:
                if d.scheduled_date and d.scheduled_date > latest_delivery.scheduled_date and d.scheduled_date < now_date:
                    latest_delivery = d
                else:
                    break
        return latest_delivery
    
    flsp_sale_orders = fields.Many2many('sale.order', string='Sales Order', compute=_get_so)
    flsp_delivery_id = fields.Many2one('stock.picking', string='Delivery', domain="[('sale_id', 'in', flsp_sale_orders)]")

    #def _get_reconciled_info_JSON_values(self):
    def _get_sale_order_info_JSON_values(self):
        self.ensure_one()
        #excluded_move_ids = AccountMoveLine.search(AccountMoveLine._get_suspense_moves_domain() + [('move_id', 'in', self.ids)]).mapped('move_id').ids
        #ids = self.env['account.move.line'].search(domain).mapped('statement_line_id').ids
        #reverse_entries = self.env['account.move'].search([('reversed_entry_id', '=', self.id)])

        if self.invoice_origin:
            so = self.env['sale.order'].search([('name', '=', self.invoice_origin.strip())])
        else:
            so = False
        contact = ''
        reconciled_vals = []
        if so:
            if so.flsp_att_to:
                contact = so.flsp_att_to.name

            for rec in so:
                reconciled_vals.append({
                    'name': rec.client_order_ref if rec.client_order_ref else rec.name,
                    'date_order': rec.date_order,
                    'flsp_ship_via': rec.flsp_ship_via,
                    'payment_term': rec.payment_term_id.note,
                    'contact': contact,
                })
        return reconciled_vals

    def _get_so_for_ci_info_JSON_values(self):
        self.ensure_one()
        so = self.env['sale.order'].search([('name', '=', self.invoice_origin.strip())])
        contact = ''
        if so.flsp_att_to:
            contact = so.flsp_att_to.name

        sale_order = []
        for rec in so:
            sale_order.append({
                'name': rec.name,
                'po': rec.client_order_ref,
                'date_order': rec.date_order,
                'flsp_ship_via': rec.flsp_ship_via,
                'payment_term': rec.payment_term_id.note,
                'contact': contact,
                'delivery': self.flsp_delivery_id.name if self.flsp_delivery_id else "",
                'ship_date': self.flsp_delivery_id.scheduled_date if self.flsp_delivery_id else "",
            })
        return sale_order
