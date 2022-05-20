# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class FlspMrpMO(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    @api.model
    def _get_default_flsp_work_center(self):
        get_wc_from_mo = False
        active_model = self.env.context.get('active_model')
        res = False
        if active_model:
            if active_model == 'mrp.production':
                get_wc_from_mo = True
        if get_wc_from_mo:
            mo_id = self.env.context.get('default_mo_id') or self.env.context.get('active_id')
            active_mo = self.env['mrp.production'].search([('id', '=', mo_id)])
            if active_mo:
                res = active_mo.flsp_mrp_work_center_id.id
        else:
            wc_id = self.env.context.get('default_flsp_mrp_work_center_id') or self.env.context.get('active_id')
            flsp_wc_id = self.env['stock.picking.type'].search([('id', '=', wc_id)], limit=1)
            if flsp_wc_id:
                res = flsp_wc_id.id
        return res

    flsp_mrp_work_center_id = fields.Many2one('flsp.mrp.work.center', string="Work Center", required=True, default=_get_default_flsp_work_center)
