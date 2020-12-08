# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspsalespartner(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True

    @api.model
    def _default_flsp_sale_currency(self):
        currency_id = self.env['res.currency'].search([('name',  '=', 'USD')])
        return currency_id

    flsp_sale_currency = fields.Many2one('res.currency', string='Sale Currency', default=_default_flsp_sale_currency, required=True)
    flsp_sale_type = fields.Selection([
        ('1', 'OEM'),
        ('2', 'Dealer'),
        ('3', 'School'),
        ('4', 'Contractor'),
        ], string='Sale Group',  default='3', required=True)

    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice Address'),
         ('delivery', 'Delivery Address'),
         ('other', 'Other Address'),
         ("private", "Private Address"),
        ], string='Address Type',
        default='delivery',
        readonly=True,
        help="Delivery addresses are used in sales orders.")

    flsp_contacts_ids = fields.One2many('flsp.contact', 'partner_id', 'Customer Contact')

    attachment_ids = fields.Many2many('ir.attachment', 'customer_attachment_rel',
        string='Attachments',
        help='Attach a new document here.')

    @api.onchange('parent_id')
    def flsp_onchange_parent_id(self):
        if not self.parent_id:
            self.type = 'contact'
            return
        self.type = 'delivery'
