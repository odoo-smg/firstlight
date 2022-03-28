# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class FlspPoContainerWizard(models.TransientModel):
    _name = 'flsp.purchase.container.po.wiz'
    _description = "Wizard: Include items of PO into Container"

    container_id = fields.Many2one('flsp.purchase.container', required=True, domain="[('status', '=', 'overseas')]")
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order', required=True,
                                  domain="[('state', '=', 'purchase')]")

    @api.model
    def default_get(self, fields):
        res = super(FlspPoContainerWizard, self).default_get(fields)
        container_id = self.env.context.get('active_id')
        if container_id:
            container = self.env['flsp.purchase.container'].browse(container_id)
        if container.exists():
            if 'container_id' in fields:
                res['container_id'] = container.id

        res = self._convert_to_write(res)
        return res

    def flsp_confirm(self):
        action = self.env.ref('flsp_purchase_container.launch_flsp_purchase_container_po_line_wiz').read()[0]
        if self.purchase_id:
            action_context = {'purchase_id': self.purchase_id.id,
                              'container_id': self.container_id.id}
            action['context'] = action_context

        return action
