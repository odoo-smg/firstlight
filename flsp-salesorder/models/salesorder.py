# -*- coding: utf-8 -*-

from odoo import fields, models


class flspsalesorder(models.Model):
    _inherit = 'sale.order'

    flsp_so_user_id = fields.Many2one('res.users', string="Salesperson 2")

    @api.onchange('partner_id')
    def flsp_partner_onchange(self):
        return {
            'value': {
                'flsp_so_user_id': self.partner_id.flsp_user_id.id
            },
        }
