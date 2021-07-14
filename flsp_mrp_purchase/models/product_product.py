# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class mrppruchaseprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    def action_view_mrp_purchase(self):
        action = self.env.ref('flsp_mrp_purchase.flsp_mrp_purchase_line_action').read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        return action

        #view_id = self.env.ref('flsp_mrp_wip.flsp_mrp_wip_wiz_form_view').id

        return {
            'name': 'WIP Transfer',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flsp.mrp.wip.wiz',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_mo_id': self.mo_id.id,
                'show_sublevels': self.show_sublevels,
                'wip_id': wip_id,
            }
        }
