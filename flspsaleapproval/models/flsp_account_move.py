# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspaccountmove(models.Model):
    _inherit = 'account.move'
    _check_company_auto = True

    flsp_broker_id = fields.Many2one('res.partner', string='Broker')
    flsp_ci_notes = fields.Text(string='Notes for Commercial Invoice')

    #def _get_reconciled_info_JSON_values(self):
    def _get_sale_order_info_JSON_values(self):
        self.ensure_one()
        #excluded_move_ids = AccountMoveLine.search(AccountMoveLine._get_suspense_moves_domain() + [('move_id', 'in', self.ids)]).mapped('move_id').ids
        #ids = self.env['account.move.line'].search(domain).mapped('statement_line_id').ids
        #reverse_entries = self.env['account.move'].search([('reversed_entry_id', '=', self.id)])


        so = self.env['sale.order'].search([('name', '=', self.invoice_origin.strip())])
        contact = ''
        if so.flsp_att_to:
            contact = so.flsp_att_to.name

        reconciled_vals = []
        for rec in so:
            reconciled_vals.append({
                'name': rec.client_order_ref if rec.client_order_ref else rec.name,
                'date_order': rec.date_order,
                'flsp_ship_via': rec.flsp_ship_via,
                'payment_term': rec.payment_term_id.note,
                'contact': contact,
            })
        return reconciled_vals

    def _get_so_for_ci_info_JSON_values(self):
        self.ensure_one()
        so = self.env['sale.order'].search([('name', '=', self.invoice_origin.strip())])
        contact = ''
        if so.flsp_att_to:
            contact = so.flsp_att_to.name

        sale_order = []
        for rec in so:
            sale_order.append({
                'name': rec.name,
                'po': rec.client_order_ref,
                'date_order': rec.date_order,
                'flsp_ship_via': rec.flsp_ship_via,
                'payment_term': rec.payment_term_id.note,
                'contact': contact,
            })
        return sale_order
