# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspChangeQtySubstitution(models.TransientModel):
    _inherit = 'change.production.qty'

    flsp_substituted = fields.Boolean('Was Substituted')

    @api.model
    def default_get(self, fields):
        res = super(flspChangeQtySubstitution, self).default_get(fields)
        if 'mo_id' in fields and not res.get('mo_id') and self._context.get('active_model') == 'mrp.production' and self._context.get('active_id'):
            res['mo_id'] = self._context['active_id']
        if 'product_qty' in fields and not res.get('product_qty') and res.get('mo_id'):
            res['product_qty'] = self.env['mrp.production'].browse(res['mo_id']).product_qty
        if 'flsp_substituted' in fields and not res.get('flsp_substituted') and res.get('mo_id'):
            res['flsp_substituted'] = self.env['mrp.production'].browse(res['mo_id']).flsp_substituted
        return res

