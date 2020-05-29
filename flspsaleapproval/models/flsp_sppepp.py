# -*- coding: utf-8 -*-

from odoo import models, fields, api


class flspsppeppmsg(models.TransientModel):
    _name = 'flspsaleapproval.sppeppmsg'
    _description = "Wizard: SPPEPP Message"

    @api.model
    def default_get(self, fields):
        res = super(flspsppeppmsg, self).default_get(fields)
        sale_order = self.env['sale.order']
        order_id = self.env.context.get('default_order_id') or self.env.context.get('active_id')
        if order_id:
            sale_order = self.env['sale.order'].browse(order_id)
        if sale_order.exists():
            flspsppepp_category_id = self.env.company.flspsppepp_category_id
            flsp_percent_sppepp = self.env.company.flsp_percent_sppepp
            amount_categ_total = 0
            for line in sale_order.order_line:
                if line.product_id.categ_id == flspsppepp_category_id:
                    amount_categ_total += line.price_subtotal

            if 'partner_id' in fields:
                res['partner_id'] = sale_order.partner_id.id
            if 'amount_total' in fields:
                res['amount_total'] = amount_categ_total
            if 'total_required' in fields:
                res['total_required'] = amount_categ_total * flsp_percent_sppepp / 100

        return res

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    amount_total = fields.Float(string='Category Total', readonly=True)
    total_required = fields.Float(string='Total Required', readonly=True)
    flspsppepp_category_id = fields.Many2one('product.category', related='company_id.flspsppepp_category_id', readonly=True, default=lambda self: self.env.company.flspsppepp_category_id)
    flsp_percent_sppepp = fields.Float(related='company_id.flsp_percent_sppepp', string="Percent of Deposit", readonly=True, default=lambda self: self.env.company.flsp_percent_sppepp)
