# -*- coding: utf-8 -*-

from odoo import models, fields, api


class product_tags(models.Model):
    _name = 'product.tags'

    name = fields.Char(string="Tag Name", required="1")


class product_template(models.Model):
    _inherit = 'product.template'

    tag_ids = fields.Many2many('product.tags', string='Tags')    # Can not group a many2many field

