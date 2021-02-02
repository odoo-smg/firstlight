# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FlspMaintenance(models.Model):
    """
        class_name: FlspMaintenance
        model_name: inherit the maintenance.equipment model
        Purpose:    To add asset # and calibration certificate #
        Date:       Feb/02/2021/T
        Author:     Sami Byaruhanga

    """
    _inherit = 'maintenance.equipment'

    flsp_asset_num = fields.Char(string="Asset #", tracking=True)
    flsp_calibration_num = fields.Char(string="Calibration Certificate #")