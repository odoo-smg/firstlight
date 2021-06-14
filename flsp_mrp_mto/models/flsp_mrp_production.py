# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

import logging


class flspproduction(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    def action_cancel(self):
        res = super(flspproduction, self).action_cancel()
        move = self.env['stock.move'].search([('mo_id', '=', self.id)])
        if move:
            move.mo_id = False
        return res
