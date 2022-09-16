# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime
import base64
import logging

_logger = logging.getLogger(__name__)


class flspCustomerBadgeaccountmove(models.Model):
    _inherit = 'account.move'
    _check_company_auto = True

    #@api.depends('line_ids.debit','line_ids.credit','line_ids.currency_id','line_ids.amount_currency',
        #'line_ids.amount_residual','line_ids.amount_residual_currency','line_ids.payment_id.state','flsp_sale_discount','flsp_freight_discount')
    #def _compute_amount(self):
        # call orginal _compute_amount() to calculate
        #super(flspCustomerBadgeaccountmove, self)._compute_amount()

        # update total amount for each invoice
        #for move in self:
            #move.amount_total = move.amount_total - move.flsp_sale_discount - move.flsp_freight_discount

    @api.depends('invoice_line_ids')
    def _compute_discount(self):
        for invoice in self:
            discount = 0
            for line in invoice.invoice_line_ids:
                discount += line.price_unit * line.quantity * line.discount / 100
            invoice.flsp_discount = discount

    @api.depends('state')
    def _compute_annual_cumulative(self):
        for invoice in self:
            #customer_invoices = self.env["account.move"].search([("partner_id", "=", invoice.partner_id.id), ("state", "=", "posted"), ('type', '=', 'out_invoice')], order='invoice_date')
            customer_invoices = self.env["account.move"].search([("partner_id", "=", invoice.partner_id.id), ("state", "=", "posted"), ('move_type', '=', 'out_invoice')], order='invoice_date')
            if len(customer_invoices) == 0:
                continue

            current_year = customer_invoices[0].invoice_date.year
            annual_cumulative = 0
            for inv in customer_invoices:
                if not inv.invoice_date:
                    continue

                inv.flsp_invoice_date = str(inv.invoice_date)

                if inv.invoice_date.year == current_year:
                    if not inv.flsp_annual_cumulative_amount or inv.flsp_annual_cumulative_amount == 0:
                        inv.flsp_annual_cumulative_amount = inv.amount_total_signed + annual_cumulative
                else:
                    current_year = inv.invoice_date.year
                    inv.flsp_annual_cumulative_amount = inv.amount_total_signed
                annual_cumulative = inv.flsp_annual_cumulative_amount

    @api.depends('state')
    def _compute_realtime_cb(self):
        for invoice in self:
            if invoice.state == 'posted':
                invoice.flsp_realtime_cb = invoice.flsp_cb_id
            else:
                invoice.flsp_realtime_cb = False

            if invoice.flsp_realtime_cb:
                invoice.flsp_realtime_cb_discount = invoice.flsp_realtime_cb.reward_level + '(' + str(
                    invoice.flsp_realtime_cb.sale_discount) + '%)'
            else:
                invoice.flsp_realtime_cb_discount = 'None'

    @api.depends('state')
    def _compute_flsp_invoice_date(self):
        for invoice in self:
            if invoice.state == 'posted':
                invoice.flsp_realtime_cb = invoice.flsp_cb_id
            else:
                invoice.flsp_realtime_cb = False

            if invoice.flsp_realtime_cb:
                invoice.flsp_realtime_cb_discount = invoice.flsp_realtime_cb.reward_level + '(' + str(
                    invoice.flsp_realtime_cb.sale_discount) + '%)'
            else:
                invoice.flsp_realtime_cb_discount = 'None'

    # fields for customer badge(cb)
    flsp_cb_id = fields.Many2one(related='partner_id.flsp_cb_id', readonly=True)
    flsp_cb_image = fields.Image(related='flsp_cb_id.image_1920', readonly=True)
    flsp_cb_sale_discount = fields.Float(related='flsp_cb_id.sale_discount', readonly=True)
    flsp_cb_freight_units_5_to_10_discount = fields.Float(related='flsp_cb_id.freight_units_5_to_10_discount',
                                                          readonly=True)
    flsp_cb_freight_units_over_10_discount = fields.Float(related='flsp_cb_id.freight_units_over_10_discount',
                                                          readonly=True)

    flsp_next_level_cb_id = fields.Many2one(related='partner_id.flsp_next_level_cb_id', readonly=True)
    flsp_next_level_amount_gap = fields.Monetary(related='partner_id.flsp_next_level_amount_gap', readonly=True)

    flsp_sale_discount = fields.Monetary(string='Reward Discount', default=0)
    flsp_freight_discount = fields.Monetary(string='Freight Discount', default=0)

    flsp_discount = fields.Monetary(string='Discount', compute=_compute_discount, store=True,
                                    help="Discount for the Invoice, including frieght")
    flsp_annual_cumulative_amount = fields.Monetary(string='Annual Cumulative', default=0,
                                                    compute=_compute_annual_cumulative, store=True)
    flsp_invoice_date = fields.Char(string="Invoice Date", compute=_compute_annual_cumulative, store=True)
    flsp_realtime_cb = fields.Many2one('flsp.customer.badge', string="Realtime Customer Badge",
                                       compute=_compute_realtime_cb, store=True)
    flsp_realtime_cb_discount = fields.Char(string="Customer Badge Disc.", compute=_compute_realtime_cb, store=True)

    # This action was created during the migration to 15
    # Some xml is calling this action and giving an error
    def button_process_edi_web_services(self):
        print('button_process_edi_web_services')