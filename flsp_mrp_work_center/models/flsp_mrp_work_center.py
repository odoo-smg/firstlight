# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FlspMrpWorkCenter(models.Model):
    _name = 'flsp.mrp.work.center'
    _description = "Work Centers of production"

    name = fields.Char(string="Name")
    mo_ids = fields.One2many(comodel_name='mrp.production', inverse_name='id', string="MOs")
    active = fields.Boolean('Active', default=True, store=True, readonly=False)
    color = fields.Integer('Color')
    mo_count = fields.Integer('# Manufacturing Orders', compute='_compute_mo_count')

    @api.depends('mo_ids', 'mo_ids.state')
    def _compute_mo_count(self):
        mos = self.env['mrp.production'].search([('flsp_mrp_work_center_id', 'in', self.ids), ('state', 'not in', ('done', 'cancel'))])

        for workcenter in self:
            count_data = 0
            for mo in mos:
                if mo.flsp_mrp_work_center_id.id == workcenter.id:
                    count_data += 1
            workcenter.mo_count = count_data

    def action_mo_tree_view(self):
        action = self.env.ref("mrp.mrp_production_tree_view").read()[0]
        return action


