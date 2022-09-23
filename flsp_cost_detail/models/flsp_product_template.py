# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class FlspCostDetProductProduct(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    def action_view_flsp_cost_detail(self):
        self.product_tmpl_id.flsp_cost_detail_recalc()
        action = self.env.ref('flsp_cost_detail.flsp_cost_detail_action').read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        return action

class FlspCostDetProductTmpl(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    def flsp_cost_detail_recalc(self):
        cost_det_list = self.env['flsp.cost.detail.view'].search([('product_tmpl_id', '=', self.id)])
        prd_id = False
        reg = 0
        total_reg = 0
        #for each in cost_det_list:
        #    if not prd_id:
        #        prd_id = each.product_id
        #    reg = reg + 1
        #if prd_id:
        query = "select count(*) as total from flsp_cost_detail_view where product_tmpl_id = '" + str(self.id) + "'"
        self._cr.execute(query)
        retvalue = self._cr.fetchall()
        if retvalue:
            total_reg = reg = retvalue[0][0]
        product = False
        reg = 1
        last_balance = False
        last_cost = False
        for line in cost_det_list:
            current_balance = 0
            current_cost = 0
            if last_balance:
                current_balance = last_balance
            if line.location_id:
                if "Virtual" in line.location_id.complete_name \
                        or "Partner" in line.location_id.complete_name \
                        or "Rejected" in line.location_id.complete_name:
                    current_balance += line.qty_done
            if line.location_dest_id:
                if "Virtual" in line.location_dest_id.complete_name \
                        or "Partner" in line.location_dest_id.complete_name \
                        or "Rejected" in line.location_dest_id.complete_name:
                    current_balance -= line.qty_done
            if last_cost:
                current_cost = last_cost
            if line.picking_type_id.id:
                if line.picking_type_id.code in ["mrp_operation", "outgoing"]:
                    if line.unit_cost > 0:
                        current_cost = line.unit_cost
                elif line.picking_type_id.code != "internal":
                    if last_balance + line.product_qty != 0:
                        current_cost = (last_cost * last_balance) + abs(line.value)
                        current_cost = current_cost / abs(last_balance + line.product_qty)
            else:
                if line.unit_cost > 0:
                    current_cost = line.unit_cost
                if "Product value manually modified" in line.reference:
                    current_cost = float(line.reference[line.reference.find(' to ') + 4:-1])
#                elif "INV" in line.reference:
#                    if line.product_qty > 0:
#                        current_cost = abs(line.value) / abs(line.product_qty)
#                else:

            cost_detail_value = False
            cost_detail_move = False
            if line.stock_valuation_layer_id:
                cost_detail_value = self.env['flsp.cost.detail'].search([('stock_valuation_layer_id', '=', line.stock_valuation_layer_id.id)])
                if cost_detail_value:
                    cost_detail_value.balance = current_balance
                    cost_detail_value.cost = current_cost
                    cost_detail_value.seq = reg
                else:
                    self.env['flsp.cost.detail'].create({
                        'picking_type_id': line.picking_type_id.id,
                        'date': line.date,
                        'location_id': line.location_id.id,
                        'location_dest_id': line.location_dest_id.id,
                        'reference': line.reference,
                        'origin': line.origin,
                        'qty_done': line.qty_done,
                        'price_unit': line.price_unit,
                        'product_qty': line.product_qty,
                        'value': line.value,
                        'unit_cost': line.unit_cost,
                        'product_id': line.product_id.id,
                        'product_tmpl_id': line.product_tmpl_id.id,
                        'balance': current_balance,
                        'cost': current_cost,
                        'seq': reg,
                        'stock_move_line_id': line.stock_move_line_id.id,
                        'stock_valuation_layer_id': line.stock_valuation_layer_id.id,
                    })
            elif line.stock_move_line_id:
                cost_detail_move = self.env['flsp.cost.detail'].search([('stock_move_line_id', '=', line.stock_move_line_id.id)])
                if cost_detail_move:
                    cost_detail_move.balance = current_balance
                    cost_detail_move.cost = current_cost
                    cost_detail_move.seq = reg
                else:
                    self.env['flsp.cost.detail'].create({
                        'picking_type_id': line.picking_type_id.id,
                        'date': line.date,
                        'location_id': line.location_id.id,
                        'location_dest_id': line.location_dest_id.id,
                        'reference': line.reference,
                        'origin': line.origin,
                        'qty_done': line.qty_done,
                        'price_unit': line.price_unit,
                        'product_qty': line.product_qty,
                        'value': line.value,
                        'unit_cost': line.unit_cost,
                        'product_id': line.product_id.id,
                        'product_tmpl_id': line.product_tmpl_id.id,
                        'balance': current_balance,
                        'cost': current_cost,
                        'seq': reg,
                        'stock_move_line_id': line.stock_move_line_id.id,
                        'stock_valuation_layer_id': line.stock_valuation_layer_id.id,
                    })
            #elif line.stock_valuation_layer_id and cost_detail_value:
            #    cost_detail_value.balance = current_balance
            #    cost_detail_value.cost = current_cost
            #    cost_detail_value.seq = reg
            else:
                self.env['flsp.cost.detail'].create({
                    'picking_type_id': line.picking_type_id.id,
                    'date': line.date,
                    'location_id': line.location_id.id,
                    'location_dest_id': line.location_dest_id.id,
                    'reference': line.reference,
                    'origin': line.origin,
                    'qty_done': line.qty_done,
                    'price_unit': line.price_unit,
                    'product_qty': line.product_qty,
                    'value': line.value,
                    'unit_cost': line.unit_cost,
                    'product_id': line.product_id.id,
                    'product_tmpl_id': line.product_tmpl_id.id,
                    'balance': current_balance,
                    'cost': current_cost,
                    'seq': reg,
                    'stock_move_line_id': line.stock_move_line_id.id,
                    'stock_valuation_layer_id': line.stock_valuation_layer_id.id,
                })
            reg = reg + 1
            last_balance = current_balance
            last_cost = current_cost


    def action_view_flsp_cost_detail(self):

        self.flsp_cost_detail_recalc()

        action = self.env.ref('flsp_cost_detail.flsp_cost_detail_action').read()[0]
        action['domain'] = [('product_tmpl_id', '=', self.id)]
        return action
