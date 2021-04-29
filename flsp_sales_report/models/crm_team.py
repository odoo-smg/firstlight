# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"
    _check_company_auto = True

    flsp_weekly_report = fields.Boolean("Weekly Report")
