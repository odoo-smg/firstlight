# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FlspSerialMrpAlertWiz(models.TransientModel):
    _name = 'flsp_serial_mrp.alert.wiz'
    _description = "Wizard: Message on Production"

    @api.model
    def default_get(self, fields):
        res = super(FlspSerialMrpAlertWiz, self).default_get(fields)
        production_order = self.env['mrp.production']
        production_id = self.env.context.get('default_production_id') or self.env.context.get('active_id')
        if production_id:
            production_order = self.env['mrp.production'].browse(production_id)
        if production_order.exists():
            if 'product_id' in fields:
                res['product_id'] = production_order.product_id.id
            if 'bom_id' in fields:
                res['bom_id'] = production_order.bom_id.id
            if 'mo_id' in fields:
                res['mo_id'] = production_order.id
        return res

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    bom_id = fields.Many2one('mrp.bom', string='Bill of Material', readonly=True)
    mo_id = fields.Many2one('mrp.production', string="MO", requiredreadonly=True)

    def flsp_button_serial_mrp_two(self):
        action = self.env.ref('flsp_serial_mrp.launch_flsp_serial_mrp_wiz_two').read()[0]
        action['res_id'] = self.mo_id.id
        return action
