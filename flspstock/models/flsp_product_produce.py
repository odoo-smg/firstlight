# -*- coding: utf-8 -*-

from odoo import fields, models, api


class flspstockproduce(models.TransientModel):
    _inherit = 'mrp.product.produce'
    _check_company_auto = True

    def action_generate_serial(self):
        self.ensure_one()
        context = {'product_id': self.product_id.product_tmpl_id}
        product_produce_wiz = self.env.ref('mrp.view_mrp_product_produce_wizard', False)
        self.finished_lot_id = self.env['stock.production.lot'].with_context(**context).create({
            'product_id': self.product_id.id,
            'company_id': self.production_id.company_id.id
        })
        return {
            'name': ('Produce'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mrp.product.produce',
            'res_id': self.id,
            'view_id': product_produce_wiz.id,
            'target': 'new',
        }
