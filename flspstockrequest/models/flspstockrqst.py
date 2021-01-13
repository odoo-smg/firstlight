# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class FlspStockRequest(models.Model):
    """
        class_name: FlspStockRequest
        model_name: flspstock.request
        Purpose:    To create stock request
        Date:       Jan/6th/2020/W
        Author:     Sami Byaruhanga
    """
    _name = 'flspstock.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Flsp Stock Requisition'

    note = fields.Char(readonly=True, default='**For production use only:\n'
                               'Transfers product from WH/STOCK to WH/PA/WIP**')
    name = fields.Char('Request Number', readonly=True, index=True, copy=False, default='New')
    date_order = fields.Datetime(string='Request Date', required=True, readonly=True, default=fields.Datetime.now)
    request_by = fields.Many2one('res.users', string="Requested by", required=True, index=True, default=lambda self: self.env.user,
                                 tracking=True)
    material_handler = fields.Many2one('res.users', ondelete='set null', string="Material Handler", index=True)
    # domain=lambda self: [('groups_id', 'in', self.env.ref('flspticketsystem.group_flspticketsystem_manager').id)],
    need_by = fields.Datetime(string='Need by', required=True, tracking=True)
    order_line = fields.One2many('flspstock.request.line', 'order_id', string='Order Lines', copy=True, auto_join=True)
    status = fields.Selection([('request', 'Request'), ('confirm', 'Confirmed'), ('done', 'Done')], default='request', eval=True, copy=False)
    is_done = fields.Boolean(store=True, compute='request_complete')
    dest_location = fields.Many2one('stock.location', string="Destination Location")
    #if we want to change dest location we simply call self in button confirm as dest location
    stock_picking = fields.Many2one('stock.picking', string='Stock Picking', copy=False, readonly=False)

    @api.onchange('need_by')
    def _check_date_greater_than_today(self):
        """
            Purpose: To ensure that the need by date is greater than the current date
        """
        for line in self:
            if line.need_by:
                if line.need_by < datetime.today():
                    raise ValidationError("The need by date must be greater than today. \n"
                                          "Please click Ok and re-enter a future date.")

    """"
        Purpose: To override default create and add sequence
    """
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            # vals['name'] = self.env['ir.sequence'].next_by_code('flspstock.request') or 'New'
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.order') or 'New'
            result = super(FlspStockRequest, self).create(vals)
        return result

    def button_confirm(self):
        """
            Purpose: To create an internal transfer
            Details: Stock picking is created and stock move are also filled.
        """

        wip_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA/WIP')])
        stock_location = self.env['stock.location'].search([('complete_name', '=', 'WH/Stock')])
        picking_type_id = self.env['stock.picking.type'].search([('sequence_code', '=', 'INT')]) #internal transfer
        if not picking_type_id:
            raise UserError('Picking type Internal is missing')
        if not wip_location:
            raise UserError('WIP Stock Location is missing')
        if not stock_location:
            raise UserError('Stock Location is missing')

        if len(self.order_line) >= 1:
            creat_val = {'picking_type_id': picking_type_id.id,
                         'origin': self.name,
                         #'scheduled_date': self.need_by,
                         'location_id': stock_location.id,
                         'location_dest_id': wip_location.id,
                         # 'partner_id': self.request_by.partner_id.id,
                         }
            stock_picking = self.env['stock.picking'].create(creat_val)
            self.message_post(body='Created Stock Transfer: '+stock_picking.name, subtype="mail.mt_note")
            # pick_lines = []
            for line in self.order_line:
                # move_lines = \
                self.env['stock.move'].create({
                    'name': line.product_id.name,
                    'origin': self.name,
                    'picking_id': stock_picking.id,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uom_qty': line.product_qty,
                    'location_id': stock_location.id,
                    'location_dest_id': wip_location.id,
                    })
                # pick_lines.append((0, 0, move_lines))
            self.stock_picking = stock_picking.id
            self.write({'status': 'confirm'})
            #stock_picking.write({'scheduled_date': self.need_by})
            stock_picking.action_assign()
        else:
            raise UserError('No transfer can be created if there is no products to transfer. \n'
                            'Click OK and fill the stock request information or delete this record')
        #stock_picking.action_confirm()
        return stock_picking

    #
    # def button_confirm(self):
    #     """
    #         Purpose: To create an internal transfer
    #         Details: Stock picking is created and stock move are also filled.
    #     """
    #     print("Running the transfer")
    #     wip_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA/WIP')])
    #     stock_location = self.env['stock.location'].search([('complete_name', '=', 'WH/Stock')])
    #     picking_type_id = 5 #internal transfer
    #     if not wip_location:
    #         raise UserError('WIP Stock Location is missing')
    #     if not stock_location:
    #         raise UserError('Stock Location is missing')
    #
    #     if len(self.order_line) >= 1:
    #         pick_lines = []
    #         for line in self.order_line:
    #             move_lines = {
    #                 'name': line.product_id.name,
    #                 'origin': self.name,
    #                 'product_id': line.product_id.id,
    #                 'product_uom': line.product_id.uom_id.id,
    #                 'product_uom_qty': line.product_qty,
    #                 'location_id': stock_location.id,
    #                 'location_dest_id': wip_location.id,
    #                 }
    #             pick_lines.append((0, 0, move_lines))
    #
    #         creat_val = {'picking_type_id': picking_type_id,
    #                      'origin': self.name,
    #                      'scheduled_date': self.need_by,
    #                      'location_id': stock_location.id,
    #                      'location_dest_id': wip_location.id,
    #                      'move_lines': pick_lines
    #                      # 'partner_id': self.request_by.partner_id.id,
    #                      }
    #         stock_picking = self.env['stock.picking'].create(creat_val)
    #         self.stock_picking = stock_picking
    #         self.write({'status': 'confirm'})
    #     else:
    #         raise UserError('No transfer can be created if there is no products to transfer. \n'
    #                         'Click OK and fill the stock request information or delete this record')
    #     stock_picking.action_confirm()
    #     return stock_picking
    #
    def view_internal_transfer(self):
        """
            Purpose: To view the internal transfer for the Stock request
        """
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        pickings = self.env['stock.picking'].search([('origin', '=', self.name)])
        form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = pickings.id
        print(self.stock_picking.origin)
        return action

    @api.depends('stock_picking','stock_picking.state')
    def request_complete(self):
        """
            Purpose: to see if the request is done
        """
        print("exectuting request_complete")
        # print(self.stock_picking.origin)
        pickings = self.env['stock.picking'].search([('origin', '=', self.name)])
        for line in self:
            if line.status == 'confirm':
                if (pickings.origin == self.stock_picking.origin) and (pickings.state == 'done'):
                    self.is_done = True
                    self.write({'status': 'done'})
                else:
                    self.is_done = False

class FlspStockRequestLine(models.Model):
    """
        Class_Name: FlspStockRequestLine
        Model_Name: flsp_sales_forecast
        Purpose:    To help create the flsp_sales_forecast
        Date:       Dec/15th/2020/W
        Updated:
        Author:     Sami Byaruhanga
    """
    _name = 'flspstock.request.line'
    order_id = fields.Many2one('flspstock.request', string='Reference', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', change_default=True) #domain=[('purchase_ok', '=', True)],
    product_qty = fields.Float(string='Demand', digits='Product Unit of Measure', required=True)
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')

    @api.onchange('product_id')
    def onchange_product_id(self):
        """
            Purpose: To be able to add the unit of measure right away
        """
        self.product_uom = self.product_id.uom_id.id
