# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

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

    flsp_required_mat_plan = fields.Boolean("Required Material", default=False)
    flsp_material_reserved = fields.Boolean("Material Reserved", default=False)

    def button_unreserve(self):
        self.flsp_material_reserved = False
        self.flsp_required_mat_plan = False
        super(Flspproduction, self).button_unreserve()

    def action_assign(self):
        super(Flspproduction, self).action_assign()
        if self.reservation_state == 'assigned':
            self.flsp_required_mat_plan = False
            self.flsp_material_reserved = True
        else:
            # check backflush reservation
            reserved_pass = True
            for each in self.move_raw_ids:
                if not each.flsp_backflush:
                    if each.product_uom_qty > each.reserved_availability:
                        reserved_pass = False
            if reserved_pass:
                self.flsp_required_mat_plan = False
                self.flsp_material_reserved = True
        return

    def flsp_require_material(self):
        self.flsp_required_mat_plan = True


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

    def _flsp_compute_material_reservation(self):
        """ Compute the material reservation state.
        """
        for production in self:
            reserved_pass = True
            production.flsp_material_reserved = False
            for each in production.move_raw_ids:
                if not each.flsp_backflush:
                    if each.product_uom_qty > each.reserved_availability:
                        reserved_pass = False
            if reserved_pass:
                production.flsp_material_reserved = True
