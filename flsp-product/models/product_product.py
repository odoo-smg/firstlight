# -*- coding: utf-8 -*-

from odoo import fields, models, api


class smgproductprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_acc_valid   = fields.Boolean(string="Accounting Validated", readonly=True, copy=False)
    attachment_ids = fields.Many2many('ir.attachment', 'product_attachment_rel','drawing_id', 'attachment_id',
        string='Attachments',
        compute='_get_product_attachment',
        store=False,
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.')
    x_studio_specification = fields.Binary(string='Specification', store=False, compute='_get_specification_attachment')
    x_studio_drawing = fields.Binary(string="Drawing", store=False, compute='_get_drawing_attachment')
    x_studio_drawing_filename = fields.Char(string="Drawing Filename", store=False)
    x_studio_specification_filename = fields.Char(string="Specification Filename", store=False)

    def button_acc_valid(self):
        self.product_tmpl_id.flsp_acc_valid = True
        return self.write({'flsp_acc_valid': True})

    def button_acc_valid_off(self):
        self.product_tmpl_id.flsp_acc_valid = False
        return self.write({'flsp_acc_valid': False})

    def _get_product_attachment(self):
        products = self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)])
        self.attachment_ids = products.attachment_ids

    def _get_specification_attachment(self):
        products = self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)])
        self.x_studio_specification = products.x_studio_specification
        self.x_studio_specification_filename = products.x_studio_specification_filename

    def _get_drawing_attachment(self):
        products = self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)])
        self.x_studio_drawing_filename = products.x_studio_drawing_filename
        self.x_studio_drawing = products.x_studio_drawing
