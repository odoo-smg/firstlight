# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class flspsostockmove(models.Model):
    _inherit = 'stock.move'

    flsp_customerscode = fields.Many2one('flspstock.customerscode', 'Customer Part Number', compute="_compute_flsp_customerscode")
    flsp_show_customercode = fields.Boolean(string="Show Customer Code", compute="_compute_flsp_show_customercode")

    def _compute_flsp_show_customercode(self):
        for each in self:
            if each.sale_line_id:
                if each.sale_line_id.order_id.flsp_show_customercode:
                    each.flsp_show_customercode = each.sale_line_id.order_id.flsp_show_customercode
                else:
                    each.flsp_show_customercode = False
            else:
                each.flsp_show_customercode = False


    def _compute_flsp_customerscode(self):
        for each in self:
            if each.sale_line_id:
                if each.sale_line_id.flsp_customerscode:
                    each.flsp_customerscode=each.sale_line_id.flsp_customerscode
                else:
                    each.flsp_customerscode = False
            else:
                each.flsp_customerscode = False



class flspstockmoveline(models.Model):
    _inherit = 'stock.move.line'

    flsp_customerscode = fields.Many2one('flspstock.customerscode', 'Customer Part Number', compute="_compute_flsp_customerscode")
    flsp_show_customercode = fields.Boolean(string="Show Customer Code", compute="_compute_flsp_show_customercode")

    def _compute_flsp_customerscode(self):
        for each in self:
            if each.move_id:
                if each.move_id.flsp_customerscode:
                    each.flsp_customerscode = each.move_id.flsp_customerscode
                else:
                    each.flsp_customerscode = False
            else:
                each.flsp_customerscode = False


    def _compute_flsp_show_customercode(self):
        for each in self:
            if each.move_id.sale_line_id:
                if each.move_id.sale_line_id.order_id.flsp_show_customercode:
                    each.flsp_show_customercode = each.move_id.sale_line_id.order_id.flsp_show_customercode
                else:
                    each.flsp_show_customercode = True
            else:
                each.flsp_show_customercode = True
