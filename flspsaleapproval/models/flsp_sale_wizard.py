# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Saleflspwizard(models.TransientModel):
    _name = 'flspsaleapproval.saleflspwizard'
    _description = "Wizard: testing my wizard"

    @api.model
    def default_get(self, fields):
        res = super(Saleflspwizard, self).default_get(fields)
        sale_order = self.env['sale.order']
        order_id = self.env.context.get('default_order_id') or self.env.context.get('active_id')
        if order_id:
            sale_order = self.env['sale.order'].browse(order_id)
        if sale_order.exists():
            if 'order_id' in fields:
                res['order_id'] = sale_order.id
            if 'validity_date' in fields:
                res['validity_date'] = sale_order.validity_date
            if 'partner_id' in fields:
                res['partner_id'] = sale_order.partner_id.id
            #if 'order_line' in fields:
            #res['order_line'] = sale_order.order_line

        approval_list = []
        for so_line in [l for l in sale_order.order_line]:
            approval_list.append([0, 0, {
                'flsp_sale_line_product_id': so_line.id,
                'sequence': so_line.sequence,
                'product_template_id': so_line.product_template_id.id,
                'product_uom_qty': so_line.product_uom_qty,
                'product_uom': so_line.product_template_id.uom_id.id,
                'price_unit': so_line.price_unit,
                'discount': so_line.discount,
                'sale_order_line_id': so_line.id,
                'tax_id': so_line.tax_id.id,
                'order_id': so_line.order_id.id,
                'price_subtotal': so_line.price_subtotal,
            }])
        res['flsp_order_line_ids'] = approval_list
        res = self._convert_to_write(res)
        return res


    order_id = fields.Many2one('sale.order', string='Order Reference', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    validity_date = fields.Date(string='Expiration')
    flsp_order_line_ids = fields.One2many('flsp.so.line', 'flsp_sale_line_product_id', string='Components')


    def flsp_approve(self):
        self.ensure_one()
        for approval_line in self.flsp_order_line_ids:
            approval_line.sale_order_line_id.write({
                'discount': approval_line.discount,
            })
            approval_line.sale_order_line_id.write({
                'price_unit': approval_line.price_unit,
            })
        self.order_id.write({'flsp_state': 'approved', })
        self.order_id.write({'flsp_approval_approved': True, })
        self.env['flspautoemails.bpmemails'].send_email(self, 'SO0002')

        self.order_id.button_flsp_confirm()

        return {'type': 'ir.actions.act_window_close'}

        body = '<p>Hi there, </p>'
        body += '<br/>'
        body += '<p>The discount approval requested for the quotation: '+self.order_id.name+' has been approved.</p>'
        body += '<br/><br/><br/>'
        body += '<br/><br/><br/>'
        body += '<div style = "text-align: center;" >'
        body += '  <a href = "https://odoo-smg-firstlight1.odoo.com/web#action=408&amp;model=sale.order&amp;view_type=list&amp;cids=1&amp;menu_id=230" style = "background: #1abc9c; padding: 20px; text-decoration: none; color: #fff; border-radius: 5px; font-size: 16px;" class ="o_default_snippet_text">Access Sales Order</a>'
        body += '  <br/><br/><br/>'
        body += '</div>'
        body += '<p>Thank you!</p>'

        self.env['mail.mail'].create({
            'body_html': body,
            'subject': 'Odoo - Sales Discount Approved',
            'email_to': 'alexandresousa@smartrendmfg.com; '+self.order_id.user_id.login,
            'auto_delete': True,
        }).send()

        return {'type': 'ir.actions.act_window_close'}

        #self.order_id.write({'validity_date': self.validity_date,})

    def flsp_open_sale_wizard(self):
        self.order_line.order_id |= self.order_id
        return {}

class FlspSOline(models.TransientModel):
    """Sales Approval"""
    _name = "flsp.so.line"
    _description = 'Edit Line on Sales Approval'

    flsp_sale_line_product_id = fields.Many2one('flspsaleapproval.saleflspwizard')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sales Order Line')
    order_id = fields.Many2one('sale.order', string='Order Reference', ondelete='cascade', index=True, copy=False)

    sequence = fields.Integer(string='Sequence', default=10)
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
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_template_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_subtotal': taxes['total_excluded'],
            })
