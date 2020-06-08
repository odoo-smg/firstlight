# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_order_option_ids = fields.One2many('sale.order.option', 'line_id', 'Optional Products Lines')
    flsp_products_line_pricelist = fields.One2many('product.product', 'id', 'Pricelist Products', compute='_calc_line_price_list_products')


    @api.depends('order_id.pricelist_id', 'sequence')
    def _calc_line_price_list_products(self):
        if 'flsp_products_pricelist' in self.env['sale.order']._fields:
            if (self.order_id.flsp_products_pricelist==False):

        for line in self:
            line.flsp_products_line_pricelist = self.order_id.flsp_products_pricelist

class SaleOrderOption(models.Model):
    _name = "sale.order.option"
    _description = "Sale Options"
    _order = 'sequence, id'

    is_present = fields.Boolean(string="Present on Quotation",
                           help="This field will be checked if the option line's product is "
                                "already present in the quotation.",
                           compute="_compute_is_present", search="_search_is_present")
    order_id = fields.Many2one('sale.order', 'Sales Order Reference', ondelete='cascade', index=True)
    line_id = fields.Many2one('sale.order.line', ondelete="set null", copy=False)
    name = fields.Text('Description', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True, domain=[('sale_ok', '=', True)])
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price')
    discount = fields.Float('Discount (%)', digits='Discount')
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure ', required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    quantity = fields.Float('Quantity', required=True, digits='Product UoS', default=1)
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of optional products.")

    @api.depends('line_id', 'order_id.order_line', 'product_id')
    def _compute_is_present(self):
        # NOTE: this field cannot be stored as the line_id is usually removed
        # through cascade deletion, which means the compute would be false
        for option in self:
            option.is_present = bool(option.order_id.order_line.filtered(lambda l: l.product_id == option.product_id))

    def _search_is_present(self, operator, value):
        if (operator, value) in [('=', True), ('!=', False)]:
            return [('line_id', '=', False)]
        return [('line_id', '!=', False)]

    @api.onchange('product_id', 'uom_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return
        product = self.product_id.with_context(lang=self.order_id.partner_id.lang)
        self.price_unit = product.list_price
        self.name = product.get_product_multiline_description_sale()
        self.uom_id = self.uom_id or product.uom_id
        pricelist = self.order_id.pricelist_id
        if pricelist and product:
            partner_id = self.order_id.partner_id.id
            self.price_unit = pricelist.with_context(uom=self.uom_id.id).get_product_price(product, self.quantity, partner_id)
        domain = {'uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        return {'domain': domain}

    def button_add_to_order(self):
        self.add_option_to_order()

    def add_option_to_order(self):
        self.ensure_one()

        sale_order = self.order_id

        if sale_order.state not in ['draft', 'sent']:
            raise UserError(_('You cannot add options to a confirmed order.'))

        values = self._get_values_to_add_to_order()
        order_line = self.env['sale.order.line'].create(values)
        order_line._compute_tax_id()

        self.write({'line_id': order_line.id})

    def _get_values_to_add_to_order(self):
        self.ensure_one()
        return {
            'order_id': self.order_id.id,
            'price_unit': self.price_unit,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': self.uom_id.id,
            'discount': self.discount,
            'company_id': self.order_id.company_id.id,
        }
