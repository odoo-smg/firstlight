# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SalesOrder(models.Model):
    _inherit = "sale.order"
    _check_company_auto = True

    flsp_approval_required  = fields.Boolean(string="Approval Required", readonly=True, compute='_calc_sale_approval')
    flsp_approval_requested = fields.Boolean(string="Approval Requested", readonly=True)
    flsp_approval_approved  = fields.Boolean(string="Discount Approved", readonly=True)
    flsp_show_discount      = fields.Boolean(string="Show Disc. on Quote")
    flsp_ship_via           = fields.Char(string="Ship Via")
    flsp_state = fields.Selection([
        ('draft', 'Quotation'),
        ('wait', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    sale_order_template_id = fields.Many2one(
        'sale.order.template', 'Quotation Template',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    sale_order_option_ids = fields.One2many(
        'sale.order.option', 'order_id', 'Optional Products Lines',
        copy=True, readonly=True,
        states={'draft': [('readonly', False)]})

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
        self.write({'flsp_approval_requested': True})
        return self.write({'flsp_state': 'wait'})

    def button_flsp_approve(self):
        #flsp_sale_order_lines = flspsaleapproval.Saleflspwizard
        #flsp_open_sale_wizard

        action = self.env.ref('flspsaleapproval.launch_flsp_sale_wizard').read()[0]
        return action

        #return self.action_confirm()

    def button_flsp_confirm(self):
        if not self.partner_id.flsp_acc_valid:
            action = self.env.ref('flspsaleapproval.launch_flsp_sale_message').read()[0]
        else:
            action = self.action_confirm()
        return action

        #return self.action_confirm()

    def button_flsp_reject(self):
        self.write({'flsp_state': 'draft'})
        self.write({'flsp_approval_approved': False})
        self.write({'flsp_approval_requested': False})
        return self.write({'flsp_approval_requested': False})

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['flsp_state'] = 'draft'
        default['flsp_approval_requested'] = False
        default['flsp_approval_approved'] = False
        default['flsp_approval_required'] = False
        return super(SalesOrder, self).copy(default=default)
