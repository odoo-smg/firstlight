import json
from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class DependingMOs(models.Model):
    _name = 'flsp.depending.mos'
    _description = "Mos Dependency (m2m)"

    task_id = fields.Many2one('mrp.production')
    depending_task_id = fields.Many2one('mrp.production')
    relation_type = fields.Selection([
        ("0", "Finish to Start"),
        ("1", "Start to Start"),
        ("2", "Finish to Finish"),
        ("3", "Start to Finish")
    ], default="0", required=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done')], default='draft')

    _sql_constraints = [
        ('mo_relation_unique', 'unique(task_id, depending_task_id)', 'Two MOs can have only one relation!'),
    ]

class GanttMO(models.Model):
    _inherit = 'mrp.production'

    planned_duration = fields.Float('Duration', compute='_compute_planned_duration', store=True)
    depending_mo_ids = fields.One2many('flsp.depending.mos', 'task_id')
    dependency_mo_ids = fields.One2many('flsp.depending.mos', 'depending_task_id')
    links_serialized_json = fields.Char('Serialized Links JSON', compute="compute_links_json")
    responsible_name = fields.Char(string='Responsible Name', related='user_id.partner_id.name')
    product_part_number = fields.Char(related='product_id.default_code')
    product_name = fields.Char(string='Product', related='product_id.name')

    recursive_dependency_mo_ids = fields.Many2many(
        string='Recursive Dependencies',
        comodel_name='mrp.production',
        compute='_compute_recursive_dependency_mo_ids'
    )

    @api.depends('date_planned_start', 'date_planned_finished')
    def _compute_planned_duration(self):
        for r in self:
            if r.date_planned_start and r.date_planned_finished:
                elapsed_seconds = (r.date_planned_finished - r.date_planned_start).total_seconds()
                seconds_in_hour = 60 * 60
                # keep it as integer for hours
                r.planned_duration = round(elapsed_seconds / seconds_in_hour, 0)
            else:
                r.planned_duration = 0

    @api.depends('dependency_mo_ids')
    def _compute_recursive_dependency_mo_ids(self):
        for mo in self:
            mo.recursive_dependency_mo_ids = mo.get_dependency_mos(
                mo, True,
            )

    @api.model
    def get_dependency_mos(self, mo, recursive=False):
        dependency_mos = mo.with_context(
            prefetch_fields=False,
        ).dependency_mo_ids
        if recursive:
            for t in dependency_mos:
                dependency_mos |= self.get_dependency_mos(t, recursive)
        return dependency_mos

    def compute_links_json(self):
        for r in self:
            links = []
            r.links_serialized_json = '['
            for link in r.dependency_mo_ids:
                json_obj = {
                    'id': link.id,
                    'source': link.task_id.id,
                    'target': link.depending_task_id.id,
                    'type': link.relation_type
                }
                links.append(json_obj)
            r.links_serialized_json = json.dumps(links)
