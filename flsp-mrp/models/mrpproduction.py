# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError
from datetime import timedelta, datetime

import logging
_logger = logging.getLogger(__name__)


class flspproduction(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain="[('flsp_plm_valid', '=', True), ('bom_ids', '!=', False), ('bom_ids.active', '=', True), ('bom_ids.type', '=', 'normal'), ('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        readonly=True, required=True, check_company=True,
        states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('planned', 'Planned'),
        ('preassemb', 'Pre Assembled'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        compute='_compute_state', copy=False, index=True, readonly=True,
        store=True, tracking=True,
        help=" * Draft: The MO is not confirmed yet.\n"
             " * Confirmed: The MO is confirmed, the stock rules and the reordering of the components are trigerred.\n"
             " * Planned: The WO are planned.\n"
             " * In Progress: The production has started (on the MO or on the WO).\n"
             " * To Close: The production is done, the MO has to be closed.\n"
             " * Done: The MO is closed, the stock moves are posted. \n"
             " * Cancelled: The MO has been cancelled, can't be confirmed anymore.")

    flsp_required_mat_plan = fields.Boolean("Required Material", default=False)
    flsp_material_reserved = fields.Boolean("Material Reserved", default=False)
    flsp_wip_transfer_ids = fields.One2many('stock.picking', inverse_name='flsp_mo_wip_id', string="Transfer Created: ")
    flsp_wip_transfer_count = fields.Integer(string='WIP Count', compute="_compute_flsp_wip_transfer_count")


    def _compute_flsp_wip_transfer_count(self):
        for each in self:
            count_transfers = 0
            for wip_transfer in each.flsp_wip_transfer_ids:
                count_transfers += 1
            each.flsp_wip_transfer_count = count_transfers

    def button_unreserve(self):
        # self.flsp_material_reserved = False
        # self.flsp_required_mat_plan = False
        super(flspproduction, self).button_unreserve()

    def button_flsp_confirm_transfer(self):
        self.flsp_material_reserved = True

    def button_flsp_cancel_transfer(self):
        self.flsp_material_reserved = False

    def action_assign(self):
        super(flspproduction, self).action_assign()
        # if self.reservation_state == 'assigned':
        #    self.flsp_required_mat_plan = False
        #    self.flsp_material_reserved = True
        # else:
            # check backflush reservation
        #    reserved_pass = True
        #    for each in self.move_raw_ids:
        #        if not each.flsp_backflush:
        #            if each.product_uom_qty > each.reserved_availability:
        #                reserved_pass = False
        #    if reserved_pass:
        #        self.flsp_required_mat_plan = False
        #        self.flsp_material_reserved = True
        return

    def flsp_require_material(self):
        if self.flsp_create_wip():
            self.flsp_required_mat_plan = True
        else:
            self.flsp_required_mat_plan = True
            self.flsp_material_reserved = True

    def flsp_create_wip(self):
        date_now = datetime.now()
        date_start = date_now.today() + timedelta(days=1)
        date_end = date_now.today() + timedelta(days=15)
        stock_picking = False
        picking_type_id = picking_id = self.env['stock.picking.type'].search([('sequence_code', '=', 'INT')], limit=1)

        targetProd = self.env['flsp.mrp.wip.wiz.product'].search(
            ['&', ('production_id', '=', self.id), ('selected', '=', True)])
        if len(targetProd) == 0:
            # targetProd = self.env['flsp.mrp.wip.wiz.comp'].search(['&', ('production_id', '=', self.id), ('selected', '=', True)])
            # targetProd = self.env['product.product'].search(['&', ('id', 'in', self.move_raw_ids.), ('selected', '=', True)])
            targetProd = self.move_raw_ids.filtered(lambda move: move.product_id.flsp_mrp_delivery_method != 'kanban' and move.product_id.type == 'product')

        count_products = 0

        for prod in targetProd:
            count_products += 1

        if count_products > 0:
            create_val = {
                'origin': self.name+'-WIP',
                'picking_type_id': picking_type_id.id,
                'location_id': picking_type_id.default_location_src_id.id,
                'location_dest_id': picking_type_id.default_location_dest_id.id,
                'flsp_mo_wip_id': self.id,
            }
            stock_picking = self.env['stock.picking'].create(create_val)

            if stock_picking:
                for prod in targetProd:
                    stock_move = self.env['stock.move'].create({
                        'name': prod.product_id.name,
                        'product_id': prod.product_id.id,
                        'product_uom': prod.product_id.uom_id.id,
                        'product_uom_qty': prod.product_uom_qty,
                        'picking_id': stock_picking.id,
                        'location_id': picking_type_id.default_location_src_id.id,
                        'location_dest_id': picking_type_id.default_location_dest_id.id,
                    })

        return stock_picking

    def action_view_wip_transfer(self):
        """ This function returns an action that display picking related to
        manufacturing order orders. It can either be a in a list or in a form
        view, if there is only one picking to show.
        """
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        pickings = self.mapped('flsp_wip_transfer_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        action['context'] = dict(self._context, default_origin=self.name, create=False)
        return action


    def flsp_pre_assembly(self):
        self.state = 'preassemb'


    @api.constrains('product_id')
    def _check_done_eco(self):
        for record in self:
            if record.product_id.flsp_plm_valid != True:
                raise exceptions.ValidationError("You cannot use products that haven't been PLM Validated yet.")
            if 'flsp_backflush' in self.env['product.template']._fields:
                if record.product_id.product_tmpl_id.flsp_backflush:
                    raise exceptions.ValidationError("You cannot use products marked as Backflush.")

    def action_confirm(self, by_pass=False):
        if by_pass:
            return super(flspproduction, self).action_confirm()
        if not self.bom_id.flsp_bom_plm_valid:
            return self.env.ref('flsp-mrp.launch_flsp_wizprd_message').read()[0]
        else:
            comps_valid = True
            for comp in self.move_raw_ids:
                if not comp.product_id.flsp_plm_valid:
                    comps_valid = False
            if not comps_valid:
                return self.env.ref('flsp-mrp.launch_flsp_mrp_comp_warning_wiz').read()[0]
            else:
                return super(flspproduction, self).action_confirm()

    def button_flsp_explode_subs(self):
        """
            Purpose: To show products with BOMS and backflush = False in a wizard
        """
        view_id = self.env.ref('flsp-mrp.products_with_boms_without_backflush_form_view').id
        return {
            'name': 'MO Products',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flspmrp.bom.structure',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_mo_id': self.id,
            }
        }

    def copy(self, default=None):
        """
            Date:    2021-06-04
            Purpose: After copy the MO, the src location of each stock.move is set with default wrong one, so reset it with MO's location_src_id
            Author:  Perry He
        """
        copied_mrp = super(flspproduction, self).copy(default=default)
        for move in copied_mrp.move_raw_ids:
            move.location_id = copied_mrp.location_src_id
        return copied_mrp

    def button_flsp_negative_forecast(self):
        """
            Purpose: To show negative forecast for Assemblies for the MO
        """
        view_id = self.env.ref('flsp-mrp.flsp_mrp_negative_forecast_wizard_form_view').id
        return {
            'name': 'Recompute Negative Forecasted Report',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flsp.mrp.negative.forecast.wizard',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_mo_id': self.id,
            }
        }

    @api.onchange('date_planned_start')
    def _onchange_date_planned_start(self):
        if not self.date_planned_start:
            raise UserError("'Planned Start Date' is required")

        super(flspproduction, self)._onchange_date_planned_start()

    #def _flsp_compute_material_reservation(self):
        #    """ Compute the material reservation state.
        #    """
        # for production in self:
        #    reserved_pass = True
        #    production.flsp_material_reserved = False
        #    for each in production.move_raw_ids:
        #        if not each.flsp_backflush:
        #            if each.product_uom_qty > each.reserved_availability:
        #                reserved_pass = False
        #    if reserved_pass:
        #        production.flsp_material_reserved = True
