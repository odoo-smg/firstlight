# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FlspApprovepowiz(models.TransientModel):
    _name = 'flsp.approve.po.wiz'
    _description = "Wizard: Approve PO"

    @api.model
    def default_get(self, fields):
        res = super(FlspApprovepowiz, self).default_get(fields)
        purchase_order = self.env['purchase.order']
        order_id = self.env.context.get('default_order_id') or self.env.context.get('active_id')
        if order_id:
            purchase_order = self.env['purchase.order'].browse(order_id)
        if purchase_order.exists():
            if 'order_id' in fields:
                res['order_id'] = purchase_order.id
            if 'partner_id' in fields:
                res['partner_id'] = purchase_order.partner_id.id

        approval_list = []
        for po_line in [l for l in purchase_order.order_line]:
            approval_list.append([0, 0, {
                'flsp_po_line_product_id': po_line.id,
                'sequence': po_line.sequence,
                'product_template_id': po_line.product_id.product_tmpl_id.id,
                'product_id': po_line.product_id.id,
                'product_uom_qty': po_line.product_qty,
                'product_uom': po_line.product_uom.id,
                'price_unit': po_line.price_unit,
                'discount': 0,
                'po_order_line_id': po_line.id,
                'tax_id': po_line.taxes_id.ids,
                'order_id': po_line.order_id.id,
                'price_subtotal': po_line.price_subtotal,
            }])
        res['flsp_order_line_ids'] = approval_list
        res = self._convert_to_write(res)
        return res


    order_id = fields.Many2one('purchase.order', string='Order Reference', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Supplier', readonly=True)
    flsp_order_line_ids = fields.One2many('flsp.po.line.wiz', 'flsp_po_line_product_id', string='Components')


    def flsp_approve(self):
        self.ensure_one()
        for approval_line in self.flsp_order_line_ids:
            approval_line.po_order_line_id.write({
                'product_qty': approval_line.product_uom_qty,
                'price_unit': approval_line.price_unit,
            })
        self.order_id.write({'flsp_po_status': 'non_confirmed', })
        self.order_id.write({'state': 'purchase', })
        self.env['flspautoemails.bpmemails'].send_email(self, 'P00006')

        self.order_id.button_approve()

        return {'type': 'ir.actions.act_window_close'}


class FlspPOline(models.TransientModel):
    """Purchase Approval"""
    _name = "flsp.po.line.wiz"
    _description = 'Edit Line on Purchase Approval'

    flsp_po_line_product_id = fields.Many2one('flsp.approve.po.wiz')
    po_order_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line')
    order_id = fields.Many2one('purchase.order', string='Order Reference', ondelete='cascade', index=True, copy=False)

    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product')
    product_template_id = fields.Many2one('product.template', string='Product Template')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    product_uom_category_id = fields.Many2one(related='product_template_id.uom_id.category_id', readonly=True)
    price_unit = fields.Float('Unit Price', digits='Product Price', default=0.0)
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id'], store=True, string='Currency',
                                  readonly=True)
    def get_approval_data(self):
        self.ensure_one()
        return {
            'flsp_sale_line_product_id': self.flsp_sale_line_product_id.id,
            'product_template_id': self.product_template_id.id,
            'sequence': self.sequence,
            'product_uom_qty': self.product_uom_qty,
            'price_unit': self.price_unit,
            'discount': self.discount,
            'sale_order_id': self.flsp_sale_line_product_id.order_id.id,
            'sale_order_line_id': self.sale_order_line_id.id,
        }

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_template_id, partner=line.order_id.partner_id)
            line.update({
                'price_subtotal': taxes['total_excluded'],
            })

