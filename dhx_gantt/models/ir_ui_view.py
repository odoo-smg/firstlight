from odoo import models, fields


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('dhx_gantt', "DHX Gantt")], ondelete={"dhx_gantt": "cascade"})
    #state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', default="draft", readonly=True, tracking=True)
    #qty_received_method = fields.Selection(selection_add=[('stock_moves', 'Stock Moves')])
