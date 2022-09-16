# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FlspSpecification(models.Model):
    """
        class_name: FlspSpecification
        model_name: flsp.specification
        Purpose:    To add specification to the product
        Date:       Dec/21st/2020/Monday
        Author:     Sami Byaruhanga

    """
    _name = 'flsp.specification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Flsp Specification"
    _rec_name = "flsp_specification_name"  # Helps to name the form view with this name

    flsp_specification_name = fields.Char(string="Name", required="1")
    flsp_specification_desc = fields.Char(string="Description")
    flsp_specification_img = fields.Many2many('ir.attachment', string='Attachment',
        help='Add the attachment')


class product_template(models.Model):
    _inherit = 'product.template'

    flsp_specification = fields.Many2many('flsp.specification', string='Family Specification')
