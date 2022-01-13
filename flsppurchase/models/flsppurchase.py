# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import float_compare
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class flsppurchase(models.Model):
    _inherit = 'purchase.order.line'
    _check_company_auto = True

    flsp_vendor_code = fields.Char('Vendor Part #')
    flsp_open_qty = fields.Float('Open Qty', compute='_open_qty_to_receive', store=True)
    flsp_product_code = fields.Char('Part #', compute='_product_code_purchase_line', store=True)
    flsp_product_desc = fields.Char('Part Description', compute='_product_desc_purchase_line', store=True)


    # Standard function  - Copied from addon to not round the currency convertion
    # Alexandre on November 8, 2021
    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return
        params = {'order_id': self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        if not seller:
            if self.product_id.seller_ids.filtered(lambda s: s.name.id == self.partner_id.id):
                self.price_unit = 0.0
            return

        price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price, self.product_id.supplier_taxes_id, self.taxes_id, self.company_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id._convert(
                price_unit, self.order_id.currency_id,
                self.order_id.company_id, self.date_order or fields.Date.today(), False)

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        self.price_unit = price_unit


    @api.onchange('product_id', 'product_qty', 'product_uom')
    def _onchange_flsp_product(self):
        for line in self:
            if not line.product_id:
                return
            params = {'order_id': self.order_id}
            vendor = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and self.order_id.date_order.date(),
                uom_id=line.product_uom,
                params=params)
            if vendor:
                line.flsp_vendor_code = vendor.product_code

    @api.depends('product_qty', 'qty_received')
    def _open_qty_to_receive(self):
        for line in self:
            line.flsp_open_qty = line.product_qty - line.qty_received


    def _product_code_purchase_line(self):
        for line in self:
            line.flsp_product_code = line.product_id.default_code

    def _product_desc_purchase_line(self):
        for line in self:
            line.flsp_product_desc = line.product_id.name
