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


    def button_flsp_confirm(self):
        if self.flsp_quote_id:
            so = env['sale.order'].search([('id', '=', record.flsp_quote_id.id)])
            if so:
            	so['flsp_amount_deposit'] = record.amount
              ## 3% credit card payment
            	if record.credit_card_payment:
            	  flspsppepp_category_id = env.company.flspsppepp_category_id
            	  flsp_percent_sppepp = env.company.flsp_percent_sppepp
            	  flspsppepp_product_id = env.company.flspsppepp_product_id
            	  sale_line_obj = env['sale.order.line']
            	  amount_categ_total = 0
            	  for line in record.flsp_quote_id.order_line:
            	    if line.product_id.categ_id == flspsppepp_category_id:
            	      amount_categ_total += line.price_subtotal

            	  context = {'lang': so.partner_id.lang}
            	  analytic_tag_ids = []
            	  for line in so.order_line:
            	    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

            	  sale_line_obj.create({
                    'name': '3% Increase CC Payment: %s',
                    'price_unit': amount_categ_total * flsp_percent_sppepp / 100 *3/100,
                    'product_uom_qty': 0.0,
                    'order_id': so.id,
                    'discount': 0.0,
                    'product_uom': flspsppepp_product_id.product_tmpl_id.uom_id.id,
                    'product_id': flspsppepp_product_id.id,
                    'analytic_tag_ids': analytic_tag_ids,
            	  })
        action = self.post()

        return action
