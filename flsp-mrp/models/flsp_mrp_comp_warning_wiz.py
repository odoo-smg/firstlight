# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FlspMrpCompWarningWiz(models.TransientModel):
    _name = 'flspmrp.comp.waring.wiz'
    _description = "Wizard: Components warning"

    @api.model
    def default_get(self, fields):
        res = super(FlspMrpCompWarningWiz, self).default_get(fields)
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
            component_list = []
            for line in production_order.move_raw_ids:
                if not line.product_id.flsp_plm_valid:
                    component_list.append([0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                }])
            res['components_ids'] = component_list

        res = self._convert_to_write(res)
        return res

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    bom_id = fields.Many2one('mrp.bom', string='Bill of Material', readonly=True)
    mo_id = fields.Many2one('mrp.production')
    components_ids = fields.One2many('flspmrp.comp.waring.line.wiz', 'flsp_wiz_id', string='Components')

    def proceed_anyways(self):
        by_pass = True
        return self.mo_id.action_confirm(by_pass)

class FlspMrpCompWarningLineWiz(models.TransientModel):
    _name = "flspmrp.comp.waring.line.wiz"
    _description = 'Substitution products for MO'
    _check_company_auto = True

    flsp_wiz_id = fields.Many2one('flspmrp.comp.waring.wiz')
    product_id = fields.Many2one('product.product', 'Component')
    product_qty = fields.Float('Quantity')
