# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api
from datetime import datetime
from odoo.exceptions import UserError


class FlspwipKanban(models.Model):
    _name = 'flsp.wip.kanban'
    _description = 'WIP Transfer'

    product_tmpl_id = fields.Many2one('product.template', string='Product template', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)

    quantity = fields.Float("Quantity")

    completed = fields.Boolean("Completed")
