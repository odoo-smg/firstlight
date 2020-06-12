# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class flsp_payment(models.Model):
    _inherit = 'account.payment'
    _check_company_auto = True

    # Add a field to validate 50% on School PPE Purchase Program
    flsp_quote_id = fields.Many2one('sale.order', string='Sale Quote',
                                    domain="['&',('partner_id', '=', partner_id),('state', '=', 'draft')]",
                                    help="Select the Quotation number to refer the 50% deposit payment for School PPE Purchase Program.")
    amount_required = fields.Float(string='Total Required', readonly=True, compute="_compute_amount_required")

    credit_card_payment = fields.Boolean(string='Credit Card Payment')

    currency_so_id = fields.Many2one('res.currency', compute='_compute_currency', string="Currency")

    @api.depends('flsp_quote_id', 'credit_card_payment')
    def _compute_amount_required(self):
        flspsppepp_category_id = self.env.company.flspsppepp_category_id
        flsp_percent_sppepp = self.env.company.flsp_percent_sppepp
        amount_categ_total = 0
        for line in self.flsp_quote_id.order_line:
            if line.product_id.categ_id == flspsppepp_category_id:
                amount_categ_total += line.price_subtotal

        if self.credit_card_payment:
            total_req_cc = amount_categ_total * flsp_percent_sppepp / 100
            self.amount_required = total_req_cc + (total_req_cc*3/100)
        else:
            self.amount_required = amount_categ_total * flsp_percent_sppepp / 100
        self.currency_so_id = self.flsp_quote_id.currency_id.id
