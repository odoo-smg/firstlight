# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Flspwipwizard(models.TransientModel):
    _name = 'flsp_wip_kanban.wizard'
    _description = "Wizard: Part Num"

    part_num = fields.Text("Part Num")

    def flsp_validate(self):
        part_num = self.part_num
        if part_num:
            part_list = part_num.split()
            for each in part_list:
                prod_tmpl_id = self.env['product.template'].search([('default_code', '=', each)])
                if prod_tmpl_id:
                    product_id = self.env['product.product'].search([('product_tmpl_id', '=', prod_tmpl_id.id)])
                    self.env['flsp.wip.kanban'].create({
                            'product_tmpl_id': prod_tmpl_id.id,
                            'product_id': product_id.id,
                            'quantity': 0,
                            'completed': False,
                        })
        kanban_to_transfer = self.env['flsp.wip.kanban'].search([('completed', '=', False)])
        kaban_count = 0
        if kanban_to_transfer:
            for kaban in kanban_to_transfer:
                kaban_count =+ 1
        if kaban_count > 0:
            action = self.env.ref('flsp_wip_transfer.launch_flsp_wip_kanban_transfer_wiz').read()[0]
            #action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
            print('calling the right thing.........')
            return action

        return

    def flsp_details_report(self):
        self.ensure_one()
        action = self.env.ref('flsp_wip_transfer.flsp_wip_transfer_action').read()[0]
        action['domain'] = [('state', '!=', 'done')]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action
