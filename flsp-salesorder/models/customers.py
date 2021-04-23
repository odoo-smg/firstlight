# -*- coding: utf-8 -*-

from odoo import fields, models


class flspcustomer(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True

    flsp_user_id = fields.Many2one('res.users', string="Inside Salesperson")
    flsp_dss_user_id = fields.Many2one('res.users', string="Dealer Specialist")

    # fields for customer badge(cb)
    flsp_cb_id = fields.Many2one('flsp.customer.badge', string="Customer Badge")
    flsp_cb_image = fields.Image(related='flsp_cb_id.image_1920', string="Customer Badge Image", readonly=True)
    flsp_cb_sale_discount = fields.Float(related='flsp_cb_id.sale_discount', readonly=True)
    flsp_cb_freight_units_5_to_10_discount = fields.Float(related='flsp_cb_id.freight_units_5_to_10_discount', readonly=True)
    flsp_cb_freight_units_over_10_discount = fields.Float(related='flsp_cb_id.freight_units_over_10_discount', readonly=True)

    flsp_shipping_method = fields.Selection([
        ('1', 'FL account and Invoice the Customer'),
        ('2', 'FL account and do not Invoice Customer'),
        ('3', 'Customer carrier choice and account'),
        ], string='Shipping Method', copy=False, store=True)

    flsp_carrier_account = fields.Char(String="Carrier Account")

    flsp_default_contact = fields.Boolean(String="Default")
    
    _sql_constraints = [
        ('customer_name_unique_flsp',
         'UNIQUE(name)',
         "The Name must be unique. Please, check the current list of customers."),
    ]

    def button_customer_badge(self):
        """
            Purpose: To call customer badge wizard with the context for the customer
        """
        view_id = self.env.ref('flsp-salesorder.manage_customer_badge_form_view').id
        name = 'Manage Customer Badge'
        customer_id = self.id
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flsp.manage.customer.badge',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_customer_id': customer_id,
            }
        }

