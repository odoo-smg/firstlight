# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from itertools import groupby


class Flsp_PO_Status(models.Model):
    """
            Class_Name: FlspStatus
            Model_Name: inherits the purchase model
            Purpose:    To help create FLSP status on Purchase
            Date:       Oct/29th/Thursday/2020
            Updated:
            Author:     Sami Byaruhanga
    """
    _inherit = 'purchase.order'

    # Change the rfq to request
    # state = fields.Selection([
    #     ('draft', 'Request'),
    #     ('sent', 'RFQ Sent'),
    #     ('to approve', 'To Approve'),
    #     ('purchase', 'Purchase Order'),
    #     ('done', 'Locked'),
    #     ('cancel', 'Cancelled')
    # ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    # Status to display on the tree view form
    flsp_po_status = fields.Selection([
        ('request', 'Request'),
        ('cancelled', 'Cancelled'),
        ('non_confirmed', 'PO Not confirmed'),
        ('confirmed', 'PO confirmed'),
        ('received', 'Received'),
        ('late', 'Late')],
        string='FLSP Status',   eval=True, store=True) #default='request',, eval=True, ('partial', 'Partially Received'),

    # Dates
    flsp_scheduled_date = fields.Datetime(string="FLSP Scheduled Date",
        help='This is the scheduled date of when the product will arrive, it accounts for product lead times'
        '\n-If multiple products, the lates product scheduled date equates to this date',
        compute="get_flsp_scheduled_date", store=True, readonly=False,)

    flsp_vendor_confirmation_date = fields.Datetime(string="Vendor Confirmation Date",
        help='This date should be entered when the Vendor has confirmed that they have shipped the order')

# STATUS
    @api.onchange('partner_id', 'date_order')  # 'date_order' is defined in addons\purchase\models\purchase.py
    def _change_status_to_request(self):
        if self.state == 'draft':
            self.write({'flsp_po_status': 'request', })
        self.write({'flsp_po_status': 'request', })

    @api.onchange('flsp_vendor_confirmation_date')
    def _change_status_to_confirmed(self):
        if self.flsp_po_status == 'cancelled':
            self.write({'flsp_po_status': 'cancelled', })
        self.write({'flsp_po_status': 'confirmed', })

# STATUS BASED OFF ORIGINAL PURCHASE BUTTONS
    # Getting the purchase button method to add status
    def button_draft(self):
        self.write({'state': 'draft'})
        self.write({'flsp_po_status': 'request', })
        return {}

    # Getting the method from the PURCHASE button and adding my status
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.company.currency_id._convert(
                        order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        if self.flsp_vendor_confirmation_date:
            order.write({'flsp_po_status': 'confirmed'})

        else:
            order.write({'flsp_po_status': 'non_confirmed'})
        return True

    # Getting the purchase button method to add status
    def button_cancel(self):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this purchase order. You must first cancel the related vendor bills."))

        self.write({'state': 'cancel'})
        self.write({'flsp_po_status': 'cancelled', })

    # Getting PURCHASE BUTTON and adding status
    def button_done(self):
        self.write({'state': 'done'})
        # self.write({'flsp_po_status': 'received', })

# DATE
    @api.onchange('flsp_vendor_confirmation_date')
    def _change_vendor_confirm_change_scheduled(self):
        """
            Purpose: On changing vendor confirmation date change the flp scheduled date
            Date:   Nov/20/2020/Friday
        """
        self.flsp_scheduled_date = self.flsp_vendor_confirmation_date

    @api.depends('date_approve', 'order_line.date_planned')
    def get_flsp_scheduled_date(self):
        """
            Purpose: To fill scheduled date field with the latest scheduled date of from the products
            NOTE:    We run the function as soon as date approved is added i.e confirm button
                     We can edit the date on actual flsp_schedule date no change on the pdct date
                     We can also edit the date on the product schedule date but change our flsp_scheduled date
        """
        if len(self.order_line) < 1:
            # print('No items')
            self.flsp_scheduled_date = False

        elif len(self.order_line) == 1:
            # print("only single item in order_line")
            self.flsp_scheduled_date = self.order_line.date_planned
        else:
            # print("we have multiple dates with length = " + str(len(self.order_line)))
            date_list = []
            for line in self.order_line:
                if line.date_planned:
                    date_list.append(line.date_planned) #adding the dates to the list
                else:
                    date_list.append(datetime.min) #adding the dates to the list

            largest_date = max(date_list)
            self.flsp_scheduled_date = largest_date

# CHANGING THE STOCK MOVE DATE BASED OFF THE SCHEDULED DATE.
    @api.depends('flsp_scheduled_date')
    def write(self, values):
        res = super().write(values)
        if "flsp_scheduled_date" in values:
            self.change_stock_scheduled_date()
        return res

    def change_stock_scheduled_date(self):
        for order in self:
            moves = self.env["stock.move"].search(
                [
                    ("purchase_line_id", "in", order.order_line.ids),
                    ("state", "not in", ("cancel", "done")),
                ]
            )
            pickings = moves.mapped("picking_id")
            pickings_by_date = {}
            for pick in pickings:
                pickings_by_date[pick.scheduled_date.date()] = pick
            order_lines = moves.mapped("purchase_line_id")
            date_groups = groupby(order_lines) #, lambda l: l._get_group_keys(l.order_id, l))
            for key, lines in date_groups:
                # date_key = fields.Date.from_string(key[0]["date_planned"])
                date_key = self.flsp_scheduled_date
                for line in lines:
                    for move in line.move_ids:
                        if move.state in ("cancel", "done"):
                            continue
                        if move.picking_id.scheduled_date.date() != date_key:
                            move.date_expected = date_key
            for picking in pickings_by_date.values():
                if len(picking.move_lines) == 0:
                    picking.write({"state": "cancel"})

# Late Status
#     @api.onchange('flsp_scheduled_date')
#     def _change_status_to_late(self):
#         # today = datetime.today().date()
#         today = datetime.today()
#         scheduled = self.flsp_scheduled_date
#         relative = relativedelta(days=-1) #past 1 day
#         if self.state == 'purchase' and (scheduled < today +relative):
#             # if(scheduled > today +relative):
#             self.write({'flsp_po_status': 'late', })
#
#         elif self.state == 'purchase' and (scheduled > today + relative) and self.flsp_vendor_confirmation_date:
#             # if(scheduled > today +relative):
#             self.write({'flsp_po_status': 'confirmed', })
#
#         elif self.state == 'purchase' and (scheduled > today + relative):
#             # if(scheduled > today +relative):
#             self.write({'flsp_po_status': 'non_confirmed', })

    # # @api.onchange('flsp_scheduled_date')
    # def _write(self, vals):
    #     # today = datetime.today().date()
    #     today = datetime.today()
    #     scheduled = self.flsp_scheduled_date
    #     relative = relativedelta(days=-1) #past 1 day
    #     if self.state == 'purchase' and (scheduled < today +relative):
    #         # if(scheduled > today +relative):
    #         self.write({'flsp_po_status': 'late', })
    #
    #     elif self.state == 'purchase' and (scheduled > today + relative) and self.flsp_vendor_confirmation_date:
    #         # if(scheduled > today +relative):
    #         self.write({'flsp_po_status': 'confirmed', })
    #
    #     elif self.state == 'purchase' and (scheduled > today + relative):
    #         # if(scheduled > today +relative):
    #         self.write({'flsp_po_status': 'non_confirmed', })


    is_shipped = fields.Boolean(string='Is shipped', compute='_compute_is_shipped', store=True)
# Changing to received got from PURCHASE.STOCK
    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_is_shipped(self):
        for order in self:
            if order.picking_ids and all([x.state in ['done', 'cancel'] for x in order.picking_ids]):
                order.is_shipped = True
                if order.state not in ['cancel', 'draft']:
                    order.write({'flsp_po_status': 'received', })
            else:
                order.is_shipped = False
