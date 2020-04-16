# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SalesOrder(models.Model):
    _inherit = "sale.order"
    _check_company_auto = True

    flsp_approval_required = fields.Boolean(string="Approval Required", readonly=True, compute='_calc_sale_approval')
    flsp_approval_requested = fields.Boolean(string="Approval Requested", readonly=True)
    flsp_approval_approved = fields.Boolean(string="Discount Approved", readonly=True)
    flsp_state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('wait', 'Waiting Approval'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('wait', 'Waiting Approval'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.depends('order_line.discount')
    def _calc_sale_approval(self):
        self.flsp_approval_required = False
        flsp_sales_discount_approval = self.env['ir.config_parameter'].sudo().get_param('flsp_sales_discount_approval')
        so_flsp_max_percent_approval = self.env.company.so_flsp_max_percent_approval
        total_discount = 0.0
        for line in self.order_line:
            if (line.discount > so_flsp_max_percent_approval) and flsp_sales_discount_approval:
                self.flsp_approval_required = True
            total_discount += line.discount

    def button_flsp_submit_approval(self):
        self.write({'flsp_state': 'wait'})
        self.write({'flsp_approval_requested': True})
        for order in self:
            tx = order.sudo().transaction_ids.get_last_transaction()
            if tx and tx.state == 'pending' and tx.acquirer_id.provider == 'transfer':
                tx._set_transaction_done()
                tx.write({'is_processed': True})
        return self.write({'state': 'done'})



    def button_flsp_approve(self):
        self.write({'flsp_state': 'sale'})
        self.write({'state': 'draft'})
        self.write({'flsp_approval_approved': True})
        return self.action_confirm()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['state'] = 'draft'
        default['flsp_state'] = 'draft'
        default['flsp_approval_requested'] = False
        default['flsp_approval_approved'] = False
        default['flsp_approval_required'] = False
        return super(SalesOrder, self).copy(default=default)

