# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class FlspMrppurchaseWizard(models.TransientModel):
    _name = 'flsp_mrp_purchase.wizard'
    _description = "Wizard: Recalculate purchase"

    calculate_sub_levels = fields.Boolean(String="Sub-Levels", default=0, help="Calculate sub-levels of BOM.")
    standard_lead_time = fields.Integer(String="Lead time", default=14, help="Standard Lead time.")
    supplier_lead_time = fields.Integer(String="Supplier Lead time", default=0, help="Supplier Lead time.")
    standard_i_lead_time = fields.Integer(String="Lead time Indirect", default=1, help="Standard Indirect Lead time.")
    standard_queue_time = fields.Integer(String="Lead time", default=1, help="Standard queue time.")
    orders_to_confirm = fields.Boolean(String="Orders to confirm", default=False)
    consider_drafts = fields.Boolean(String="Consider Draft MOs", default=False)
    consider_wip = fields.Boolean(String="Consider WIP balance", default=False)
    consider_forecast = fields.Boolean(String="Consider Forecast", default=True)
    consider_reserved = fields.Boolean(String="Consider Reserved", default=False)
    consider_mos = fields.Boolean(String="Consider Manufacturing Orders", default=False)
    consider_sales = fields.Boolean(String="Consider Sales Orders", default=True)

    @api.model
    def default_get(self, fields):
        res = super(FlspMrppurchaseWizard, self).default_get(fields)
        mrp_draft = self.env['mrp.production'].search([('state', 'in', ['draft'])])
        if mrp_draft.exists():
            if 'orders_to_confirm' in fields:
                res['orders_to_confirm'] = True

        res = self._convert_to_write(res)
        return res

    def flsp_report(self):
        self.ensure_one()
        date = datetime.now()
        result = ''
        dictionary = {'mo': self.env['flsp.mrp.purchase.line'].search([('adjusted_qty', '>', 0)], order="required_by")}

        result += '''<p>Hi there, here is the list of all products suggested to buy: </p>
            <table  class="table table-md"style="padding: 0px ">
                <tr>
                    <th style="padding-left: 10px; border-collapse:collapse; background:#203764;border: 1px solid #ddd; color: #fff; ">Product</th>
                    <th style="padding-left: 10px; border-collapse:collapse; background:#203764;border: 1px solid #ddd; color: #fff; ">Required Qty</th>
                    <th style="padding-left: 10px; border-collapse:collapse; background:#203764;border: 1px solid #ddd; color: #fff; ">UofM</th>
                    <th style="padding-left: 10px; border-collapse:collapse; background:#203764;border: 1px solid #ddd; color: #fff; ">Required by</th>
                    <th style="padding-left: 10px; border-collapse:collapse; background:#203764;border: 1px solid #ddd; color: #fff; ">Qty on Hand</th>
                </tr>

                '''
        style_reg = 'style="padding-left: 10px; border-collapse:collapse; border: 1px solid #ddd; "'
        style_red = 'style="padding-left: 10px; border-collapse:collapse; border: 1px solid #ddd; background-color: #FBE7D9"'
        date_now = (str(date))[0:10]

        for line in dictionary['mo']:
            date2 = str(line.required_by)
            date_com = date2[0:10]
            if date_com < date_now:
                style = style_red
            else:
                style = style_reg

        result += '<tr>'
        result += '<td ' + style + '>' + line.product_id.default_code + " - " + line.product_id.name + '</td>'
        result += '<td ' + style + '>' + str(line.adjusted_qty) + '</td>'
        result += '<td ' + style + '>' + line.uom.name + '</td>'
        result += '<td ' + style + '>' + date_com + '</td>'
        result += '<td ' + style + '>' + str(line.product_qty) + '</td>'
        result += '</tr>'
        result += '</table> <br/>'

        print(result)

        action = self.env.ref('flsp_mrp_purchase.flsp_mrp_purchase_line_action').read()[0]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action

    def flsp_recalc(self):
        #self.env['flsp.mrp.purchase.line']._flsp_calc_purchase(self.calculate_sub_levels, self.standard_lead_time, self.standard_queue_time, self.standard_i_lead_time, self.consider_drafts)
        self.env['flsp.mrp.purchase.line']._flsp_calc_purchase(self.supplier_lead_time, self.standard_lead_time, self.standard_queue_time, self.standard_i_lead_time, self.consider_drafts, self.consider_wip, self.consider_forecast, self.consider_mos, self.consider_sales, self.consider_reserved)

        #product = self.env['product.product'].search([], limit=1)
        #product._flsp_calc_suggested_qty()
        #action = self.env.ref('flsppurchase.purchase_suggestion_action').read()[0]
        action = self.env.ref('flsp_mrp_purchase.flsp_mrp_purchase_line_action').read()[0]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action

    def flsp_confirm_mo(self):
        print('confirming')
        mrp_draft = self.env['mrp.production'].search([('state', 'in', ['draft'])])
        for mo in mrp_draft:
            print('confirming mo: '+mo.name)
            mo.action_confirm()
        self.orders_to_confirm = False
        return {
            "type": "ir.actions.act_window",
            "name": "MRP purchase",
            "view_mode": "form",
            "res_model": "flsp_mrp_purchase.wizard",
            "view_id": self.env.ref(
                "flsp_mrp_purchase.flsp_mrp_purchase_wizard_form_view"
            ).id,
            "target": "new",
            "res_id": self.id,
        }
