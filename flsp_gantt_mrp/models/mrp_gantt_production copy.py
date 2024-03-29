import json
from datetime import timedelta

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class DependingMOs(models.Model):
    _name = "flsp.depending.mos"
    _description = "Mos Dependency (m2m)"

    # mo_id = fields.Many2one('mrp.production')
    task_id = fields.Many2one('mrp.production')
    # depending_mo_id = fields.Many2one('mrp.production')
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


    # @api.onchange('task_id')
    # def _onchange_task_id(self):
    #     if self.task_id:
    #         self.mo_id = self.task_id

    # @api.onchange('depending_task_id')
    # def _onchange_depending_task_id(self):
    #     if self.depending_task_id:
    #         self.depending_mo_id = self.depending_task_id

class GanttMO(models.Model):
    _inherit = "mrp.production"

    planned_duration = fields.Float('Duration', default=7, compute='_compute_planned_duration', inverse='_inverse_planned_duration', store=True)
    lag_time = fields.Integer('Lag Time')
    depending_mo_ids = fields.One2many('flsp.depending.mos', 'task_id')
    dependency_mo_ids = fields.One2many('flsp.depending.mos', 'depending_task_id')
    links_serialized_json = fields.Char('Serialized Links JSON', compute="compute_links_json")
    date_start = fields.Datetime('Start Date', compute="_compute_gantt_dates", store=True)
    date_end = fields.Datetime('End Date', compute="_compute_gantt_dates", store=True)
    project_id = fields.Many2one('project.project', default=False, string='Project')

    recursive_dependency_mo_ids = fields.Many2many(
        string='Recursive Dependencies',
        comodel_name='mrp.production',
        compute='_compute_recursive_dependency_mo_ids'
    )

    # @api.model
    # def default_get(self, fields):
    #     self.env.context['default_project_id'] = True
    #     _logger.info("default_project_id=" + str(self.env.context.get('default_project_id', False)))

    #     return super(GanttMO, self).default_get(fields)

    @api.depends('date_planned_start', 'date_planned_finished')
    def _compute_gantt_dates(self):
        for mo in self:
            mo.date_start = mo.date_planned_start
            mo.date_end = mo.date_planned_finished

    @api.depends('date_start', 'date_end')
    def _compute_planned_duration(self):
        for r in self:
            if r.date_start and r.date_end:
                elapsed_seconds = (r.date_end - r.date_start).total_seconds()
                seconds_in_day = 24 * 60 * 60
                r.planned_duration = elapsed_seconds / seconds_in_day
                r = r.with_context(ignore_onchange_planned_duration=True)

    @api.onchange('date_start', 'date_end')
    def _onchange_dates(self):
        for r in self:
            if r.date_start and r.date_end:
                r.date_planned_start = r.date_start
                r.date_planned_finished = r.date_end

    @api.onchange('planned_duration', 'date_start')
    def _inverse_planned_duration(self):
        # ignore_onchange_planned_duration = self.env.context.get('ignore_onchange_planned_duration', False)
        # _logger.info("ignore_onchange_planned_duration=" + str(ignore_onchange_planned_duration))
        for r in self:
            if r.date_start and r.planned_duration and not self.env.context.get('ignore_onchange_planned_duration', False):
                r.date_end = r.date_start + timedelta(days=r.planned_duration)

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
