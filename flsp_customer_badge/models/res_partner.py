# -*- coding: utf-8 -*-

from odoo import fields, models, api


class flspcustomerbadgepartner(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True

    # fields for customer badge(cb)
    participate_in_cb = fields.Boolean(String="Participate in Customer Badge", default=True,
                                       help="By unchecking the field, you will not participate in the 'Customer Badge Program'")
    flsp_cb_id = fields.Many2one('flsp.customer.badge', string="Customer Badge")
    flsp_cb_image = fields.Image(related='flsp_cb_id.image_1920', string="Customer Badge Image", readonly=True)
    flsp_cb_sale_discount = fields.Float(related='flsp_cb_id.sale_discount', readonly=True)
    flsp_cb_freight_units_5_to_10_discount = fields.Float(related='flsp_cb_id.freight_units_5_to_10_discount',
                                                          readonly=True)
    flsp_cb_freight_units_over_10_discount = fields.Float(related='flsp_cb_id.freight_units_over_10_discount',
                                                          readonly=True)

    flsp_sale_group = fields.Selection([
        ('1', 'OEM'),
        ('2', 'Dealer'),
        ('3', 'School'),
        ('4', 'Contractor'),
        ], string='Sale Type', compute='_compute_flsp_sales_group')


    def _compute_flsp_sales_group(self):
        if 'flsp_sale_type' in self.env['res.partner']._fields:
            self.flsp_sale_group = self.flsp_sale_type
        else:
            self.flsp_sale_group = '2'

    @api.onchange('participate_in_cb')
    def _onchange_participate_in_cb(self):
        if self.flsp_cb_id:
            # update current badge in record/history if it exists
            current_record = self.env['flsp.customer.badge.record'].search(
                [('customer_id', '=', self.id), ('flsp_cb_id', '=', self.flsp_cb_id.id), ('end_date', '=', False)],
                order='start_date desc', limit=1)
            if current_record:
                current_record.end_date = self.write_date

            # remove current badge for customer
            self.flsp_cb_id = False

    def flsp_get_next_level(self, current_cb):
        if (not current_cb) or (not current_cb.reward_level):
            return self.env['flsp.customer.badge'].search([('reward_level', '=', 'BRONZE')], limit=1)
        elif current_cb.reward_level == 'BRONZE':
            return self.env['flsp.customer.badge'].search([('reward_level', '=', 'SILVER')], limit=1)
        elif current_cb.reward_level == 'SILVER':
            return self.env['flsp.customer.badge'].search([('reward_level', '=', 'GOLD')], limit=1)
        elif current_cb.reward_level == 'GOLD':
            return self.env['flsp.customer.badge'].search([('reward_level', '=', 'PLATINUM')], limit=1)
        elif current_cb.reward_level == 'PLATINUM':
            return current_cb
        else:
            return current_cb

    @api.depends('flsp_cb_id')
    def _compute_next_level(self):
        for customer in self:
            customer.flsp_next_level_cb_id = self.flsp_get_next_level(customer.flsp_cb_id)

    flsp_next_level_cb_id = fields.Many2one('flsp.customer.badge', string="Next Level Badge",
                                            compute=_compute_next_level)
    flsp_next_level_amount_gap = fields.Monetary(string='Amount Gap to Next Level Badge',
                                                 help="Amount Gap to move to the next level of Customer Badge")

    def button_customer_badge(self):
        """
            Purpose: To call customer badge wizard with the context for the customer
        """
        view_id = self.env.ref('flsp_customer_badge.manage_customer_badge_form_view').id
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

    def action_view_account_summary(self):
        action = self.env.ref('flsp_customer_badge.flsp_action_customer_account_move_summary').read()[0]
        action['domain'] = [('partner_id', '=', self.id), ('state', '=', 'posted'), ('type', '=', 'out_invoice')]
        return action
